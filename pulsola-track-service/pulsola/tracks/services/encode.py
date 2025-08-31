import asyncio
import base64
import binascii
import enum
import io
import string
import uuid
from collections.abc import Generator

import orjson
import tortoise.exceptions
from opentelemetry import trace
from pydantic import BaseModel, ValidationError

from pulsola.tracks.database.models import Tracks
from pulsola.tracks.enum import TrackStatus
from pulsola.tracks.services.download import VALID_CHARS
from pulsola.tracks.services.s3 import Buckets, S3Service


class SupportedFormats(enum.StrEnum):
    FLAC = 'flac'
    WAVE = 'wav'


FFMPEG_FLAC_CMD = string.Template(
    # 'ffmpeg -f ${input_format} -i ${input_path} -map 0:a:0 -vn -dn -sn '
    'ffmpeg -loglevel -8 -f ${input_format} -i ${input_path} -map 0:a:0 -vn -dn -sn '
    '-af "silenceremove=stop_periods=1:stop_duration=1:stop_threshold=-90dB" '
    '-f flac ${output_path}'
)
FFMPEG_CMD = string.Template(
    # "ffmpeg -f ${input_format} -i ${input_path} -b:a ${bitrate}k -map 0:a:0 -vn -dn -sn "
    'ffmpeg -loglevel -8 -f ${input_format} -i ${input_path} -b:a ${bitrate}k -map 0:a:0 -vn -dn -sn '
    '-af "silenceremove=stop_periods=1:stop_duration=1:stop_threshold=-90dB" '
    '-f ogg ${output_path}'
)
FFPROBE_CMD = string.Template(
    'ffprobe -loglevel -8 -of json -show_error -show_format -select_streams a:0 -i ${file_path}'
)
FFPROBE_BINARY_CMD = (
    'ffprobe -loglevel -8 -of json -show_error -show_format -select_streams a:0 -i -'
)
BITRATES = (96, 160, 320)
tracer = trace.get_tracer('pulsola.ffmpeg')


class FFmpegError(BaseModel):
    code: int
    string: str


class FFmpegFormat(BaseModel):
    filename: str
    nb_streams: int
    nb_programs: int
    format_name: str
    duration: float | None = None
    bit_rate: int | None = None
    probe_score: int


class FFmpegResult(BaseModel):
    format: FFmpegFormat | None = None
    error: FFmpegError | None = None


class FFMpegEncoder:
    path: str
    dir: str
    encoded: str
    uuid_: uuid.UUID

    def __init__(self, tmp_path: str, file_path: str, track_id: str):
        assert isinstance(file_path, str), 'Only str is are accepted for file_path'
        assert isinstance(tmp_path, str), 'Only str is accepted for tmp_path'
        self.path = file_path
        self.dir = tmp_path

        self.encoded = track_id
        self.uuid_ = self.decode_track_id(track_id)

    @classmethod
    def generate_track_id(cls) -> tuple[uuid.UUID, str]:
        new_uuid = uuid.uuid4()
        encoded = base64.urlsafe_b64encode(new_uuid.bytes)
        return new_uuid, encoded.decode()[:-2]

    @classmethod
    def encode_track_id(cls, uuid_: uuid.UUID) -> str:
        return base64.urlsafe_b64encode(uuid_.bytes).decode()

    @classmethod
    def decode_track_id(cls, encoded: str) -> uuid.UUID:
        try:
            return uuid.UUID(bytes=base64.urlsafe_b64decode(encoded + '=='))
        except binascii.Error:
            raise ValueError('Invalid encoding')
        except ValueError as e:
            raise e

    async def probe(self) -> tuple[bool, SupportedFormats | None, int | float]:
        proc = await asyncio.subprocess.create_subprocess_shell(
            FFPROBE_CMD.substitute(file_path=self.path), stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        try:
            result = FFmpegResult.model_validate(orjson.loads(stdout.decode()))
        except (ValidationError, orjson.JSONDecodeError) as e:
            raise RuntimeError(
                f'ffprobe returned invalid data:\n{stdout.decode()}\n{e}'
            )
        if result.error is not None:
            raise RuntimeError(
                f'ffprobe failed: {result.error.code} {result.error.string}'
            )
        if result.format is None:
            raise RuntimeError(f'ffprobe returned invalid data:\n{stdout.decode()}')

        assert result.format.duration

        match result.format.format_name:
            case SupportedFormats.FLAC:
                return True, SupportedFormats.FLAC, result.format.duration
            case SupportedFormats.WAVE:
                assert result.format.bit_rate
                return True, SupportedFormats.WAVE, result.format.duration
        return False, None, -1

    @staticmethod
    async def probe_binary(file: io.BytesIO) -> tuple[bool, SupportedFormats | None]:
        proc = await asyncio.subprocess.create_subprocess_shell(
            FFPROBE_BINARY_CMD,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate(input=file.getbuffer())
        try:
            result = FFmpegResult.model_validate(orjson.loads(stdout.decode()))
        except (ValidationError, orjson.JSONDecodeError) as e:
            raise RuntimeError(
                f'ffprobe returned invalid data:\n{stdout.decode()}\n{e}'
            )
        if result.error is not None:
            raise RuntimeError(
                f'ffprobe failed: {result.error.code} {result.error.string}'
            )
        if result.format is None:
            raise RuntimeError(f'ffprobe returned invalid data:\n{stdout.decode()}')

        match result.format.format_name:
            case SupportedFormats.FLAC:
                return True, SupportedFormats.FLAC
            case SupportedFormats.WAVE:
                return True, SupportedFormats.WAVE
        return False, None

    async def convert_to_ogg(
            self, input_format: SupportedFormats, bitrate: int, bucket: Buckets
    ) -> str:
        key = f'{self.dir}/{bitrate}.ogg'
        if bucket not in Buckets.ogg_buckets():
            raise ValueError('Invalid bucket argument for OGG file')

        proc = await asyncio.create_subprocess_shell(
            FFMPEG_CMD.substitute(
                input_format=input_format,
                input_path=self.path,
                bitrate=bitrate,
                output_path=key,
            )
        )
        await proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f'ffmpeg failed: {proc.returncode}')
        return key

    async def convert_to_flac(self, input_format: SupportedFormats) -> str:
        key = f'{self.dir}/raw.flac'
        proc = await asyncio.create_subprocess_shell(
            FFMPEG_FLAC_CMD.substitute(
                input_format=input_format, input_path=self.path, output_path=key
            )
        )
        await proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f'ffmpeg failed: {proc.returncode}')
        return key

    async def process(self) -> None:
        with tracer.start_as_current_span('ffmpeg.process'):
            try:
                (is_supported, probed_format, _), record = await asyncio.gather(
                    self.probe(), Tracks.get(id=self.uuid_)
                )
            except tortoise.exceptions.DoesNotExist:
                raise ValueError(f'Track {self.uuid_} does not exist')

            if not is_supported or not probed_format:
                raise ValueError('This file is not supported')
            record.status = TrackStatus.PROCESSING
            await record.save()
            oggs = await asyncio.gather(
                *[
                    self.convert_to_ogg(probed_format, bitrate, bucket)
                    for bitrate, bucket in zip(BITRATES, Buckets.ogg_buckets())
                ]
            )

            async with S3Service() as s3:
                flac_path = await self.convert_to_flac(probed_format)
                (_, _, duration), _ = await asyncio.gather(
                    FFMpegEncoder(
                        tmp_path=self.dir, file_path=flac_path, track_id=self.encoded
                    ).probe(),
                    s3.upload_file(
                        flac_path, Bucket=Buckets.RAW_TRACKS, Key=f'{self.encoded}.flac'
                    ),
                )
                record.duration = round(duration)
                async with asyncio.TaskGroup() as tg:
                    for path, bucket in zip(oggs, Buckets.ogg_buckets()):
                        tg.create_task(
                            s3.upload_file(
                                path, Bucket=bucket, Key=f'{self.encoded}.ogg'
                            )
                        )

            record.status = TrackStatus.READY
            await record.save()


def sanitize_title(title: str) -> str:
    def _gen(_title: str) -> Generator[str, None]:
        for c in _title:
            if c in VALID_CHARS:
                yield c
            else:
                yield '-'

    return ''.join(_gen(title))
