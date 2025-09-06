from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from ossia.tracks.database.models import Creators
from ossia.tracks.datamodels.creators import CreatorInfo
from ossia.tracks.dependencies import get_creator, get_creator_secure

router = APIRouter(prefix='/{creator_id}')


@router.get('/', response_model_exclude_none=True)
async def get_creator_info(
        creator: Annotated[Creators, Depends(get_creator)],
) -> CreatorInfo:
    await creator.fetch_related('tags')
    return CreatorInfo.model_validate(creator, from_attributes=True)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_creator(
        creator: Annotated[Creators, Depends(get_creator_secure)],
) -> None:
    creator.is_active = False
    await creator.save()


@router.get('/avatar')
async def get_creator_avatar(creator: Annotated[Creators, Depends(get_creator)]):
    pass


@router.put('/avatar')
async def put_creator_avatar(creator: Annotated[Creators, Depends(get_creator_secure)]):
    pass


@router.delete('/avatar')
async def delete_creator_avatar(
        creator: Annotated[Creators, Depends(get_creator_secure)],
):
    pass


@router.get('/banner')
async def get_creator_banner(creator: Annotated[Creators, Depends(get_creator)]):
    pass


@router.put('/banner')
async def put_creator_banner(creator: Annotated[Creators, Depends(get_creator_secure)]):
    pass


@router.delete('/banner')
async def delete_creator_banner(
        creator: Annotated[Creators, Depends(get_creator_secure)],
):
    pass
