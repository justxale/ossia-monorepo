import asyncio
from typing import Annotated

import tortoise.exceptions
from fastapi import HTTPException, Security
from fastapi.routing import APIRouter
from starlette import status

from ossia.common.propdict import PropDict
from ossia.tracks.database.models import Creators, Tags
from ossia.tracks.datamodels.creators import CreateCreator, CreatorInfo, UserCreators
from ossia.tracks.dependencies import User, auth_user

router = APIRouter()


@router.get('/', response_model_exclude_none=True)
async def get_creators(user: Annotated[User, Security(auth_user)]) -> UserCreators:
    props = PropDict()
    props['creators'] = await Creators.filter(owner=user.oid)
    return UserCreators.model_validate(props, from_attributes=True)


@router.post('/')
async def create_creator(
        user: Annotated[User, Security(auth_user)], body: CreateCreator
) -> CreatorInfo:
    if body.url:
        try:
            await Creators.get(url=body.url)
            raise HTTPException(status.HTTP_409_CONFLICT, 'This URL is already claimed')
        except tortoise.exceptions.DoesNotExist:
            pass
    creator = await Creators.create(
        display_name=body.display_name,
        url=body.url,
        description=body.description,
        owner=user.oid,
    )
    if body.tags and any(body.tags):
        records, _ = zip(
            *(
                await asyncio.gather(
                    *[Tags.get_or_create(value=tag.lower()) for tag in body.tags]
                )
            )
        )

        await creator.tags.add(*records)
    await creator.fetch_related('tags')

    res = PropDict()
    res['id'] = creator.id
    res['display_name'] = creator.display_name
    res['record_url'] = creator.url
    res['description'] = creator.description
    res['tags'] = map(lambda x: getattr(x, 'value'), creator.tags)
    res['has_banner'] = creator.has_banner
    res['has_avatar'] = creator.has_avatar

    return CreatorInfo.model_validate(res, from_attributes=True)
