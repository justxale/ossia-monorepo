import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from faststream.rabbit import RabbitBroker
from starlette import status

from ossia.users.database.models import Users
from ossia.users.routes.broker import router
from ossia.users.services.auth import AuthService

scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/users/oauth/token')


def get_broker() -> RabbitBroker:
    """
    Returns broker created by RabbitRouter integration
    :return: RabbitBroker
    """
    return router.broker


async def auth_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(scheme)]) -> Users:
    return await AuthService.full_token_auth(token)


def decode_uuid(user_id: str) -> uuid.UUID:
    try:
        return AuthService.decode_uuid(user_id)
    except ValueError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, 'Invalid user id')
