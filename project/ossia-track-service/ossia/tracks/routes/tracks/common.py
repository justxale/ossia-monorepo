from typing import Annotated

from fastapi import APIRouter, Query

from ossia.common.propdict import PropDict
from ossia.tracks.database.models import Tracks
from ossia.tracks.datamodels.tracks import TracksResponse
from ossia.tracks.enum import TrackVisibility

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
