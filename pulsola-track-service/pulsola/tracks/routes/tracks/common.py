from typing import Annotated

from fastapi import APIRouter, Query

from pulsola.common.propdict import PropDict
from pulsola.tracks.database.models import Tracks
from pulsola.tracks.datamodels.tracks import TracksResponse
from pulsola.tracks.enum import TrackVisibility

router = APIRouter()


@router.get('/')
async def get_tracks(
        limit: Annotated[int, Query()] = 20,
        offset: Annotated[int, Query()] = 0,
        tags: Annotated[list[str] | None, Query()] = None,
) -> TracksResponse:
    query = Tracks.filter(visibility=TrackVisibility.PUBLIC, creator__is_active=True)
    if tags:
        query = query.filter(tags__in=tags)
    tracks = await query.prefetch_related('creator').offset(offset).limit(limit)
    data = PropDict()
    data['tracks'] = tracks
    return TracksResponse.model_validate(data, from_attributes=True)
