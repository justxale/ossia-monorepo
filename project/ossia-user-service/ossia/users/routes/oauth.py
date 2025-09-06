from typing import Annotated

import tortoise.exceptions
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from ossia.users.database.models import Users
from ossia.users.schemas.users import SignUp, Token
from ossia.users.services.auth import AuthService

router = APIRouter(prefix='/oauth', tags=['user'])


@router.post('/register')
async def register(data: SignUp, response: Response) -> Token:
    user = await AuthService.create_user(data.username, data.display_name, data.password)
    exp, jwt = AuthService.encode_jwt(user)
    response.set_cookie('access_token', jwt, expires=exp, samesite='strict')
    return Token(access_token=jwt)


@router.get('/register', status_code=status.HTTP_204_NO_CONTENT)
async def check_username(u: Annotated[str, Query()]):
    if await Users.exists(username=u):
        raise HTTPException(status.HTTP_409_CONFLICT, 'Username already claimed')
    return


@router.post('/token')
async def login(
        data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response
) -> Token:
    user = await AuthService.full_pwd_auth(data.username, data.password)
    exp, jwt = AuthService.encode_jwt(user)
    response.set_cookie('access_token', jwt, expires=exp, samesite='strict')
    return Token(access_token=jwt)
