import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, computed_field

from pulsola.users.config import UserServiceConfig
from pulsola.users.services.auth import AuthService

PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^+=_\-()])[A-Za-z\d@$!%*?&#^+=_\-()]{8,}$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')


class UserSocial(BaseModel):
    title: str = Field(min_length=1, max_length=64)
    value: str = Field(min_length=1, max_length=64)


class UserProfile(BaseModel):
    oid: UUID = Field(alias='id', exclude=True)
    username: str
    display_name: str
    has_avatar: bool = False

    @computed_field()
    @property
    def id(self) -> str:
        return AuthService.encode_uuid(self.oid)
    # avatar_url: str | None = Field(default=None, max_length=256)

    # @field_validator('avatar_url')
    # @classmethod
    # def validate_avatar_url(cls, value: str | None) -> str | None:
    #     if value and not value.startswith('http'):
    #         raise ValueError('Field avatar_url must be a valid URL')
    #     return value


class UserProfileEdit(BaseModel):
    display_name: str | None = Field(default=None, max_length=64)
    password: str | None = Field(default=None, min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        # Can't use pattern in field because error: look-around, including look-ahead and look-behind, is not supported
        if not re.match(PASSWORD_PATTERN, value):
            raise ValueError(
                'The password must contain Latin letters, at least one uppercase letter, one lowercase letter, '
                'one number and special character.'
            )

        return value


class SignUp(BaseModel):
    display_name: str = Field(max_length=64)
    username: str = Field(min_length=4, max_length=32, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        # Can't use pattern in field because error: look-around, including look-ahead and look-behind, is not supported
        if not re.match(PASSWORD_PATTERN, value):
            raise ValueError(
                'The password must contain Latin letters, at least one uppercase letter, one lowercase letter, '
                'one number and special character.'
            )

        return value


class Token(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_in: int = UserServiceConfig().jwt_ttl_seconds
