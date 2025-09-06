from fastapi import HTTPException
from faststream.exceptions import RejectMessage
from faststream.rabbit.fastapi import RabbitRouter
from pydantic import ValidationError

from ossia.common.propdict import PropDict
from ossia.users.config import UserServiceConfig
from ossia.users.schemas.broker import UserAuthMessage, UserResponse
from ossia.users.services.auth import AuthService

router = RabbitRouter(UserServiceConfig().rabbit_dsn)


@router.subscriber('access-token-check', retry=3)
async def auth_user(msg: UserAuthMessage) -> UserResponse:
    try:
        data = PropDict()
        data['user'] = await AuthService.full_token_auth(msg.token)
        data['code'] = 200
    except HTTPException as e:
        data = PropDict()
        data['code'] = e.status_code
        data['error'] = e.detail
    try:
        return UserResponse.model_validate(data, from_attributes=True)
    except ValidationError:
        raise RejectMessage()
