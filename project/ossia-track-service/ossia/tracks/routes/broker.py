import asyncio
import tempfile

from faststream.exceptions import AckMessage
from faststream.rabbit.fastapi import RabbitRouter
from faststream.rabbit.opentelemetry import RabbitTelemetryMiddleware
from opentelemetry import metrics, trace
from pydantic import BaseModel

from ossia.tracks.config import TracksServiceConfig
from ossia.tracks.services.covers import process_cover
from ossia.tracks.services.encode import FFMpegEncoder
from ossia.tracks.services.s3 import Buckets, S3Service

router = RabbitRouter(
    TracksServiceConfig().rabbit_dsn,
    max_consumers=5,
    middlewares=(
        RabbitTelemetryMiddleware(
            tracer_provider=trace.get_tracer_provider(),
            meter_provider=metrics.get_meter_provider(),
        ),
    ),
)


class ProcessingRequest(BaseModel):
    track_id: str
    cover_key: str | None = None
    audio_key: str


async def process_cover_and_track(
        track_id: str, audio_key: str, cover_key: str | None
) -> None:
    if cover_key is None:
        raise TypeError('cover_key must be str')

    tmp = tempfile.TemporaryDirectory()

    try:
        async with S3Service() as s3:
            await asyncio.gather(
                s3.download_file(
                    Bucket=Buckets.BUFFER,
                    Key=audio_key,
                    Filename=f'{tmp.name}/{audio_key}',
                ),
                s3.download_file(
                    Bucket=Buckets.BUFFER,
                    Key=cover_key,
                    Filename=f'{tmp.name}/{cover_key}',
                ),
            )
        ffmpeg = FFMpegEncoder(
            tmp_path=tmp.name, file_path=f'{tmp.name}/{audio_key}', track_id=track_id
        )

        async with asyncio.TaskGroup() as tg:
            tg.create_task(ffmpeg.process())
            tg.create_task(process_cover(f'{tmp.name}/{cover_key}', track_id))

        async with S3Service() as s3:
            await asyncio.gather(
                s3.delete_object(Bucket=Buckets.BUFFER, Key=audio_key),
                s3.delete_object(Bucket=Buckets.BUFFER, Key=cover_key),
            )
    finally:
        tmp.cleanup()


async def process_track(track_id: str, audio_key: str) -> None:
    tmp = tempfile.TemporaryDirectory(delete=False)
    try:
        async with S3Service() as s3:
            await s3.download_file(
                Bucket=Buckets.BUFFER, Key=audio_key, Filename=f'{tmp.name}/{track_id}'
            )
        print('File downloaded')
        ffmpeg = FFMpegEncoder(
            file_path=f'{tmp.name}/{track_id}', track_id=track_id, tmp_path=tmp.name
        )
        await ffmpeg.process()
        async with S3Service() as s3:
            await s3.delete_object(Bucket=Buckets.BUFFER, Key=audio_key)
    finally:
        tmp.cleanup()
        pass


@router.subscriber('track-process', no_reply=True)
async def launch_track_processing(body: ProcessingRequest) -> None:
    if body.cover_key is None:
        t = asyncio.create_task(process_track(body.track_id, body.audio_key))
        await asyncio.sleep(0)
        await t
        raise AckMessage()

    t = asyncio.create_task(
        process_cover_and_track(body.track_id, body.audio_key, body.cover_key)
    )
    await asyncio.sleep(0)
    await t

    raise AckMessage()
