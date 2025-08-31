import uuid
from typing import Annotated

import tortoise
from fastapi import Depends, HTTPException
from starlette import status
from tortoise.expressions import Q

from pulsola.tracks.database.models import Creators, Tracks
from pulsola.tracks.dependencies.security import User, auth_user, optionally_auth_user
from pulsola.tracks.enum import TrackVisibility
from pulsola.tracks.services.encode import FFMpegEncoder


async def get_track_secure(
        track_id: str, user: Annotated[User, Depends(auth_user)]
) -> Tracks:
    try:
        track_uuid = FFMpegEncoder.decode_track_id(track_id)
        return await Tracks.get(
            Q(
                Q(visibility=TrackVisibility.PRIVATE)
                | Q(visibility=TrackVisibility.DRAFT),
                creator__owner=user.oid,
            )
            | Q(is_public=True),
            id=track_uuid,
            creator__is_active=True,
        )
    except (ValueError, tortoise.exceptions.DoesNotExist):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Track not found')


async def get_track(
        track_id: str, user: Annotated[User | None, Depends(optionally_auth_user)]
):
    if user is not None:
        return await get_track_secure(track_id, user)
    try:
        track_uuid = FFMpegEncoder.decode_track_id(track_id)
        return await Tracks.get(is_public=True, id=track_uuid, creator__is_active=True)
    except (ValueError, tortoise.exceptions.DoesNotExist):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Track not found')


async def get_creator_secure(
        creator_id: str, user: Annotated[User, Depends(auth_user)]
) -> Creators:
    try:
        if creator_id[0] == '@':
            creator = await Creators.get(url=creator_id[1:], owner=user.oid)
        else:
            creator = await Creators.get(id=uuid.UUID(hex=creator_id), owner=user.oid)
    except (tortoise.exceptions.DoesNotExist, ValueError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Creator not found')
    if not creator.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Creator is queued for deletion')
    return creator


async def get_creator(
        creator_id: str, user: Annotated[User | None, Depends(optionally_auth_user)]
) -> Creators:
    if user is not None:
        return await get_creator_secure(creator_id, user)

    try:
        if creator_id[0] == '@':
            creator = await Creators.get(url=creator_id[1:], is_active=True)
        else:
            creator = await Creators.get(id=uuid.UUID(hex=creator_id), is_active=True)
    except (tortoise.exceptions.DoesNotExist, ValueError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Creator not found')
    return creator
