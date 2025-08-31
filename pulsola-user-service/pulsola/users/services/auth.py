from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from uuid import UUID

import argon2.exceptions
import jwt
import tortoise.exceptions
from argon2 import PasswordHasher
from fastapi import HTTPException
from fastapi.security.http import HTTPBearer
from pydantic import BaseModel, computed_field
from starlette import status

from pulsola.users.config import UserServiceConfig
from pulsola.users.database.models import Users

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=401,
    detail='Invalid credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)

USER_AUTH_SCHEME = HTTPBearer(scheme_name='Users', auto_error=False)
JWT_ALGORITHM = 'HS256'
JWT_ISSUER = "ossia"


class TokenPayload(BaseModel):
    iat: datetime
    exp: datetime
    iss: str
    sub: str

    # scope: str

    # display_name: str | None
    # username: str

    @computed_field()
    @property
    def user_uuid(self) -> UUID:
        return AuthService.decode_uuid(self.sub + '==')

    # @computed_field
    # @property
    # def scopes(self) -> list[str]:
    #     if self.scope:
    #         return self.scope.split()
    #     return []


class AuthService:
    @classmethod
    def jwt_timestamps(cls) -> tuple[datetime, datetime]:
        """
        :return: A tuple of IAT and EXP JWT stamps
        """
        config = UserServiceConfig()
        now = datetime.now(tz=timezone.utc)
        return now, now + timedelta(hours=config.jwt_ttl_hours)

    @classmethod
    def hash(cls, pwd: str) -> bytes:
        hasher = PasswordHasher()
        return hasher.hash(pwd).encode()

    @classmethod
    def verify_pwd(cls, pwd: str | bytes, _hash: str | bytes) -> bool:
        hasher = PasswordHasher()
        try:
            return hasher.verify(hash=_hash, password=pwd)
        except (
                argon2.exceptions.InvalidHashError, argon2.exceptions.VerificationError,
                argon2.exceptions.VerifyMismatchError
        ):
            return False

    @classmethod
    def check_for_rehash(cls, _hash: str | bytes) -> bool:
        hasher = PasswordHasher()
        return hasher.check_needs_rehash(_hash)

    @classmethod
    def encode_jwt(cls, user: Users) -> tuple[datetime, str]:
        config = UserServiceConfig()
        iat, exp = cls.jwt_timestamps()
        payload = TokenPayload(iat=iat, exp=exp, sub=cls.encode_uuid(user.id), iss=JWT_ISSUER)

        return (
            exp, jwt.encode(
                payload=payload.model_dump(exclude={'user_uuid'}), key=config.jwt_secret_key, algorithm=JWT_ALGORITHM
            )
        )

    @classmethod
    def decode_jwt(cls, token: str) -> TokenPayload:
        config = UserServiceConfig()

        payload = jwt.decode(jwt=token, key=config.jwt_secret_key, algorithms=[JWT_ALGORITHM], issuer=JWT_ISSUER)
        return TokenPayload.model_validate(payload)

    @classmethod
    def encode_uuid(cls, uuid: UUID) -> str:
        raw = urlsafe_b64encode(uuid.bytes).decode('utf-8')
        return raw[:-2]

    @classmethod
    def decode_uuid(cls, encoded_id: str) -> UUID:
        raw = encoded_id + '=='
        decoded = urlsafe_b64decode(raw.encode('utf-8'))
        return UUID(bytes=decoded)

    @classmethod
    async def full_token_auth(cls, token: str) -> Users:
        try:
            payload = cls.decode_jwt(token)
            return await Users.get(id=payload.user_uuid)
        except (jwt.PyJWTError, tortoise.exceptions.DoesNotExist):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid access token')

    @classmethod
    async def full_pwd_auth(cls, username: str, pwd: str) -> Users:
        exc = HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid credentials')
        try:
            user = await Users.get(username=username)
        except tortoise.exceptions.DoesNotExist:
            raise exc
        if not cls.verify_pwd(pwd=pwd, _hash=user.password_hash):
            raise exc
        if cls.check_for_rehash(user.password_hash):
            user.password_hash = cls.hash(pwd)
            await user.save()
        return user

    @classmethod
    async def create_user(cls, username: str, display_name: str, password: str) -> Users:
        if await Users.exists(username=username):
            raise HTTPException(status.HTTP_409_CONFLICT, 'Username already exists')

        _hash = cls.hash(password)
        user = await Users.create(
            username=username, display_name=display_name, password_hash=_hash
        )
        return user
