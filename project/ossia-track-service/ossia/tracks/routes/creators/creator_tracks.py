import asyncio
import io
import uuid
from datetime import datetime
from typing import Annotated, AsyncGenerator, Literal

from aiobotocore.response import StreamingBody
from aioitertools import enumerate as aenumerate
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    Query,
    Security,
    UploadFile,
)
from faststream.rabbit import RabbitBroker
from starlette import status
from starlette.responses import StreamingResponse
from tortoise.functions import Count
from tortoise.queryset import ValuesListQuery

from ossia.common.propdict import PropDict
from ossia.tracks.database.models import Creators, Tracks
from ossia.tracks.datamodels.tracks import (
    DownloadTracks,
    TrackInfo,
    TracksResponse,
)
from ossia.tracks.dependencies import (
    User,
    auth_user,
    get_broker,
    get_creator,
    optionally_auth_user,
)
from ossia.tracks.enum import DownloadType, TrackVisibility
from ossia.tracks.routes.broker import ProcessingRequest
from ossia.tracks.services.covers import CoverFormats, probe_cover
from ossia.tracks.services.download import create_files_zip
from ossia.tracks.services.encode import FFMpegEncoder, sanitize_title
from ossia.tracks.services.s3 import Buckets, S3Service


async def _body_gen(
        counter_len: int,
        values_gen: AsyncGenerator[tuple[uuid.UUID, str], None]
                    | ValuesListQuery[Literal[False]],
) -> AsyncGenerator[tuple[str, StreamingBody], None]:
    async with S3Service() as s3:
        async for i, (track_id, title) in aenumerate(values_gen):
            encoded_id = FFMpegEncoder.encode_track_id(track_id)
            body = (
                await s3.get_object(Bucket=Buckets.RAW_TRACKS, Key=f'{encoded_id}.flac')
            )['Body']
            yield f'{i:0>{counter_len}}-{sanitize_title(title)}.flac', body


router = APIRouter(prefix='/{creator_id}/tracks')


@router.get('/')
async def get_creator_tracks(
        creator: Annotated[Creators, Depends(get_creator)],
        user: Annotated[User | None, Security(optionally_auth_user)],
        limit: Annotated[int, Query()] = 10,
        offset: Annotated[int, Query()] = 0,
) -> TracksResponse:
    query = Tracks.filter(creator=creator)
    if not user or user.oid != creator.owner:
        query = query.filter(visibility=TrackVisibility.PUBLIC)
    data = PropDict()
    data['tracks'] = await query.offset(offset).limit(limit)
    return TracksResponse.model_validate(data, from_attributes=True)


@router.post('/')
async def upload_track(
        tasks: BackgroundTasks,
        broker: Annotated[RabbitBroker, Depends(get_broker)],
        creator_id: str,
        creator: Annotated[Creators, Depends(get_creator)],
        user: Annotated[User, Security(auth_user)],
        title: Annotated[str, Form()],
        track: UploadFile,
        description: Annotated[str | None, Form()] = None,
        cover: UploadFile | str | None = None,
) -> TrackInfo:
    if user.oid != creator.owner:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f'You cannot publish track for creator {creator_id}',
        )
    track_io = io.BytesIO(await track.read())
    is_supported, probed_format = await FFMpegEncoder.probe_binary(track_io)
    uuid_, encoded = FFMpegEncoder.generate_track_id()
    if not is_supported:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Only WAV and FLAC files supported'
        )
    audio_key = f'{encoded}/audio.{probed_format}'
    record = await Tracks.create(
        id=uuid_, title=title, description=description, creator=creator
    )

    if not isinstance(cover, UploadFile):
        async with S3Service() as s3:
            await s3.upload_fileobj(track_io, Bucket=Buckets.BUFFER, Key=audio_key)
        msg = ProcessingRequest(track_id=encoded, audio_key=audio_key, cover_key=None)
        tasks.add_task(broker.publish, msg, 'track-process')
        return TrackInfo.model_validate(record, from_attributes=True)

    cover_io = io.BytesIO(await cover.read())
    cover_format = probe_cover(cover_io)
    if not cover_format or cover_format not in (CoverFormats.JPEG, CoverFormats.PNG):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            'Only PNG and JPEG files are supported',
        )

    cover_key = f'{encoded}/cover.{cover_format}'
    async with S3Service() as s3:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                s3.upload_fileobj(track_io, Bucket=Buckets.BUFFER, Key=audio_key)
            )
            tg.create_task(
                s3.upload_fileobj(cover_io, Bucket=Buckets.BUFFER, Key=cover_key)
            )

    msg = ProcessingRequest(track_id=encoded, audio_key=audio_key, cover_key=cover_key)
    tasks.add_task(broker.publish, msg, 'track-process')
    return TrackInfo.model_validate(record, from_attributes=True)


@router.post('/download')
async def download_creator_tracks(
        creator: Annotated[Creators, Depends(get_creator)],
        user: Annotated[User, Security(auth_user)],
        body: DownloadTracks,
) -> StreamingResponse:
    if user.oid != creator.owner:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    now = datetime.now().date().strftime('%m-%d-%y')

    match body.action:
        case DownloadType.SELECTED:
            assert isinstance(body.track_ids, list)
            query = Tracks.filter(
                creator=creator,
                id__in=(
                    FFMpegEncoder.decode_track_id(track_id)
                    for track_id in body.track_ids
                ),
            )
        case DownloadType.ALL:
            query = Tracks.filter(creator=creator)
        case _:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid action')

    count_len = len(
        str(
            await query.annotate(count=Count('id'))
            .first()
            .values_list('count', flat=True)
        )
    )

    gen = create_files_zip(
        count_len, _body_gen(count_len, query.values_list('id', 'title', flat=True))
    )

    return StreamingResponse(
        gen,
        media_type='application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename={creator.id.hex}-tracks-{now}.zip'
        },
    )
