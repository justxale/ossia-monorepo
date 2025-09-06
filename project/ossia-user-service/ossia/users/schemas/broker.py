import uuid

from pydantic import BaseModel, Field


class UserAuthMessage(BaseModel):
    token: str


class BrokerUser(BaseModel):
    username: str = Field(max_length=32)
    oid: uuid.UUID = Field(alias='id')


class UserResponse(BaseModel):
    code: int
    user: BrokerUser = None
    error: str | None = None
