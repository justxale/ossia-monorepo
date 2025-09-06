import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from starlette import status

from ossia.users.database.models import Users, UserSocials
from ossia.users.dependencies import auth_user, decode_uuid
from ossia.users.schemas.users import UserProfileEdit, UserProfile, UserSocial
from ossia.users.services.auth import AuthService

router = APIRouter(prefix='/me')


@router.get('/')
async def user_profile(user: Annotated[Users, Depends(auth_user)]) -> UserProfile:
    return UserProfile.model_validate(user, from_attributes=True)


@router.patch('/')
async def edit_profile(user: Annotated[Users, Depends(auth_user)], data: UserProfileEdit) -> UserProfile:
    if data.password:
        user.password_hash = AuthService.hash(pwd=data.password)

    await user.update_from_dict(
        data.model_dump(exclude_unset=True, exclude={'password'})
    )
    await user.save()

    return UserProfile.model_validate(user, from_attributes=True)


@router.get('/socials')
async def my_socials(user: Annotated[Users, Depends(auth_user)]) -> list[UserSocial]:
    return [
        UserSocial(title=social.title, value=social.value)
        for social in await user.socials.all()
    ]


@router.patch('/socials')
async def edit_socials(user: Annotated[Users, Depends(auth_user)], data: list[UserSocial]) -> list[UserSocial]:
    await user.socials.all().delete()
    new_socials: list[UserSocials] = await asyncio.gather(*[
        UserSocials.create(title=social.title, value=social.value, user=user) for social in data
    ])

    return [UserSocial.model_validate(social, from_attributes=True) for social in new_socials]


@router.get('/balance')
async def my_balance(user: Annotated[Users, Depends(auth_user)]):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/statistics')
async def my_statistics(user: Annotated[Users, Depends(auth_user)]):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
