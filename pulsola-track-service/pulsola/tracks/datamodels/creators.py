import re
import uuid
from typing import Annotated

from pydantic import BaseModel, Field, computed_field
from pydantic.types import StringConstraints

URL_TAG_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')


class CreateCreator(BaseModel):
    display_name: str = Field(max_length=32)
    url: str | None = Field(None, max_length=32, min_length=4, pattern=URL_TAG_PATTERN)
    description: str | None = Field(None, max_length=2 ** 11)

    tags: (
            list[
                Annotated[
                    str,
                    StringConstraints(
                        strip_whitespace=True,
                        to_lower=True,
                        pattern=URL_TAG_PATTERN,
                        max_length=32,
                        min_length=2,
                    ),
                ]
            ]
            | None
    ) = None


class ShortCreatorInfo(BaseModel):
    oid: uuid.UUID = Field(alias='id')
    display_name: str
    record_url: str | None = Field(None, exclude=True)
    description: str | None = None

    has_avatar: bool

    @computed_field()
    @property
    def url(self) -> str:
        if self.record_url:
            return f'@{self.record_url}'
        return self.oid.hex


class CreatorInfo(ShortCreatorInfo):
    tags: (
            list[
                Annotated[
                    str,
                    StringConstraints(
                        strip_whitespace=True,
                        to_lower=True,
                        pattern=URL_TAG_PATTERN,
                        max_length=32,
                        min_length=2,
                    ),
                ]
            ]
            | None
    ) = None
    has_banner: bool


class UserCreators(BaseModel):
    creators: list[ShortCreatorInfo]
