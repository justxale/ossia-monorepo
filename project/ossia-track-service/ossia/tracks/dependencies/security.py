import uuid
from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from faststream.rabbit import RabbitBroker
from pydantic import BaseModel, Field, ValidationError
from starlette import status

from ossia.tracks.dependencies import get_broker

scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/users/oauth/token', auto_error=False)


class UserAuthMessage(BaseModel):
    token: str


class User(BaseModel):
    username: str = Field(max_length=32)
    oid: uuid.UUID = Field(alias='id')


class UserResponse(BaseModel):
    code: int
    user: User | None = None
    error: str | None = None


async def _request_user(token: str, broker: RabbitBroker) -> User:
    try:
        msg = await broker.request(
            UserAuthMessage(token=token), queue='access-token-check', timeout=5
        )
    except TimeoutError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, 'Unable to verify user'
        )

    try:
        decoded = await msg.decode()
        assert isinstance(decoded, dict)
        res = UserResponse.model_validate(decoded)
    except (AssertionError, ValidationError) as e:
        print(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 'Unable to verify user'
        )
    if res.code != 200 or not res.user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User is unauthorized')
    return res.user


async def auth_user(
        token: Annotated[str, Depends(scheme)],
        broker: Annotated[RabbitBroker, Depends(get_broker)],
) -> User:
    return await _request_user(token, broker)


async def optionally_auth_user(
        token: Annotated[str | None, Depends(scheme)],
        broker: Annotated[RabbitBroker, Depends(get_broker)],
) -> User | None:
    if not token:
        return None
    user = await _request_user(token, broker)
    return user
