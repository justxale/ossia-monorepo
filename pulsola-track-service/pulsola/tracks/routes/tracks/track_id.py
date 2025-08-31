import asyncio
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends, Header
from starlette import status
from starlette.responses import StreamingResponse

from pulsola.tracks.database.models import Tags, Tracks
from pulsola.tracks.datamodels.tracks import TrackInfo, UpdateTrack
from pulsola.tracks.dependencies import get_track, get_track_secure
from pulsola.tracks.services.s3 import Buckets, S3Service

BYTES_PER_REQEUST = 512 * 1024
router = APIRouter(prefix='/{track_id}')


@router.get('/')
async def get_track_info(track: Annotated[Tracks, Depends(get_track)]) -> TrackInfo:
    await track.fetch_related('creator')
    return TrackInfo.model_validate(track, from_attributes=True)


@router.put('/')
async def update_track_info(
        track: Annotated[Tracks, Depends(get_track_secure)], body: UpdateTrack
) -> TrackInfo:
    cleaned = body.model_dump(exclude_unset=True)
    if new_title := cleaned.get('title'):
        track.title = new_title
    if new_description := cleaned.get('description'):
        track.description = new_description
    if new_tags := cleaned.get('tags'):
        new_tags: list[str]  # type: ignore[no-redef]
        records, _ = zip(
            *(
                await asyncio.gather(
                    *[Tags.get_or_create(value=tag.lower()) for tag in new_tags]
                )
            )
        )

        await track.tags.add(*records)
    await track.save()
    await track.fetch_related('creator')
    return TrackInfo.model_validate(track, from_attributes=True)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(track: Annotated[Tracks, Depends(get_track_secure)]) -> None:
    await track.delete()


@router.get('/cover')
async def get_track_cover(
        track_id: str, track: Annotated[Tracks, Depends(get_track)],
        size: Annotated[Literal[256, 512, 1024, 2048, 3000], Query()] = 256
):
    if not track.has_cover:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'No cover for this track')
    async with S3Service() as s3:
        res = await s3.get_object(
            Bucket=Buckets.COVERS, Key=f'{track_id}/cover{size}.jpg'
        )
    return StreamingResponse(res['Body'], status_code=status.HTTP_200_OK, media_type='image/jpeg')


async def get_stream(track_id: str, start: int, end: int) -> StreamingResponse:
    async with S3Service() as s3:
        try:
            res = await s3.get_object(
                Bucket=Buckets.OGG_160, Key=f'{track_id}', Range=f'bytes={start}-{end}'
            )
            headers = {
                'Content-Range': res['ContentRange'],
                'Accept-Ranges': 'bytes',
                'Content-Length': str(res['ContentLength']),
            }
            return StreamingResponse(
                res['Body'],
                status_code=status.HTTP_206_PARTIAL_CONTENT,
                media_type='audio/ogg',
                headers=headers,
            )
        except Exception:
            raise HTTPException(
                status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                'Requested Range Not Satisfiable',
            )


@router.get('/playback', status_code=status.HTTP_206_PARTIAL_CONTENT)
async def stream_track(
        track_id: str,
        track: Annotated[Tracks, Depends(get_track)],
        _range: Annotated[str | None, Header(alias='range')] = None,
) -> StreamingResponse:
    if _range is None:
        return await get_stream(track_id, 0, BYTES_PER_REQEUST - 1)

    try:
        byte_range = _range.strip().lower().replace('bytes=', '')
        start_str, end_str = byte_range.split('-')
        start = int(start_str)
        end = int(end_str) if end_str else BYTES_PER_REQEUST - 1 + start
    except Exception:
        raise HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, 'Invalid Range header'
        )

    return await get_stream(track_id, start, end)
