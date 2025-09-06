import asyncio.subprocess
import base64
import binascii
import enum
import io
import string
import uuid

import orjson
from opentelemetry import trace
from pydantic import BaseModel, ValidationError, model_validator

from ossia.tracks.database.models import Tracks
from ossia.tracks.enum import TrackStatus
from ossia.tracks.services.download import VALID_CHARS
from ossia.tracks.services.s3 import Buckets, S3Service


class SupportedFormats(enum.StrEnum):
    FLAC = 'flac'
    WAVE = 'wav'


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

    @model_validator(mode='after')
    def model_check(self):
        print(self.format_name, self.duration, self.bit_rate)
        if self.format_name == 'flac' and not self.duration:
            raise ValueError('Missing duration for flac')
        if self.format_name == 'wav' and not self.bit_rate:
            raise ValueError('Missing bit_rate for wav')
        return self


class FFmpegResult(BaseModel):
    format: FFmpegFormat | None = None
    error: FFmpegError | None = None


FFMPEG_FLAC_CMD = string.Template(
    'ffmpeg -loglevel -8 -f ${input_format} -i - -map 0:a:0 -vn -dn -sn '
    '-af "silenceremove=stop_periods=1:stop_duration=1:stop_threshold=-90dB" '
    '-c:a flac -f flac pipe:1'
)
FFMPEG_CMD = string.Template(
    'ffmpeg -loglevel -8 -f ${input_format} -i - -b:a ${bitrate}k -map 0:a:0 -vn -dn -sn '
    '-af "silenceremove=stop_periods=1:stop_duration=1:stop_threshold=-90dB" '
    '-c:a ogg -f flac -'
)
FFPROBE_CMD = (
    'ffprobe -loglevel -8 -of json -show_error -show_format -select_streams a:0 -i -'
)
BITRATES = (96, 160, 320)
tracer = trace.get_tracer('ossia.ffmpeg')


class FFmpegController:
    _file: io.BytesIO
    encoded: str
    uuid_: uuid.UUID

    def __init__(self, file: bytes | io.BytesIO, track_id: str | None = None):
        if isinstance(file, io.BytesIO):
            self._file = file
        elif isinstance(file, bytes):
            self._file = io.BytesIO(file)
        else:
            raise TypeError('Only bytes or io.BytesIO are accepted')

        if track_id:
            self.encoded = track_id
            self.uuid_ = self.decode_track_id(track_id)
        else:
            self.uuid_, self.encoded = self.generate_track_id()

    @classmethod
    def generate_track_id(cls) -> tuple[uuid.UUID, str]:
        new_uuid = uuid.uuid4()
        encoded = base64.urlsafe_b64encode(new_uuid.bytes)
        return new_uuid, encoded.decode()[:-2]

    @classmethod
    def encode_track_id(cls, uuid_: uuid.UUID) -> str:
        return base64.urlsafe_b64encode(uuid_.bytes).decode()

    @classmethod
    def decode_track_id(cls, encoded: str):
        try:
            return uuid.UUID(bytes=base64.urlsafe_b64decode(encoded + '=='))
        except binascii.Error:
            raise ValueError('Invalid encoding')
        except ValueError as e:
            raise e

    async def probe(self) -> tuple[bool, SupportedFormats | None, int | float]:
        proc = await asyncio.subprocess.create_subprocess_shell(
            FFPROBE_CMD, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate(input=self._file.getbuffer())
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
                return True, SupportedFormats.FLAC, result.format.duration
            case SupportedFormats.WAVE:
                return True, SupportedFormats.WAVE, result.format.bit_rate
        return False, None, -1

    async def convert_to_ogg(
            self, input_format: SupportedFormats, bitrate: int, bucket: Buckets
    ) -> bytes:
        if bucket not in Buckets.ogg_buckets():
            raise ValueError('Invalid bucket argument for OGG file')

        proc = await asyncio.create_subprocess_shell(
            FFMPEG_CMD.substitute(input_format=input_format, bitrate=bitrate),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate(input=self._file.getbuffer())
        if proc.returncode != 0:
            raise RuntimeError('ffmpeg failed')
        return stdout

    async def convert_to_flac(self, input_format: SupportedFormats):
        proc = await asyncio.create_subprocess_shell(
            FFMPEG_FLAC_CMD.substitute(input_format=input_format),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate(input=self._file.getbuffer())
        if proc.returncode != 0:
            raise RuntimeError('ffmpeg failed')
        return stdout

    async def process(self):
        with tracer.start_as_current_span('ffmpeg.process'):
            (is_supported, probed_format, _), record = await asyncio.gather(
                self.probe(), Tracks.get(id=self.uuid_)
            )
            if not is_supported or not probed_format:
                raise ValueError('This file is not supported')
            record.status = TrackStatus.PROCESSING
            await record.save()
            tasks = [
                self.convert_to_ogg(probed_format, bitrate, bucket)
                for bitrate, bucket in zip(BITRATES, Buckets.ogg_buckets())
            ]

            async with S3Service() as s3:
                _io = io.BytesIO(await self.convert_to_flac(probed_format))
                (_, _, duration), _ = await asyncio.gather(
                    FFmpegController(file=_io, track_id=self.encoded).probe(),
                    s3.upload_fileobj(
                        _io, Bucket=Buckets.RAW_TRACKS, Key=f'{self.encoded}.flac'
                    ),
                )
                record.duration = round(duration)
                for task, bucket in zip(tasks, Buckets.ogg_buckets()):
                    await s3.upload_fileobj(
                        _io, Bucket=bucket, Key=f'{self.encoded}.ogg'
                    )

            record.status = TrackStatus.READY
            await record.save()


def sanitize_title(title: str):
    def _gen(_title: str):
        for c in _title:
            if c in VALID_CHARS:
                yield c
            else:
                yield '-'

    return ''.join(_gen(title))
