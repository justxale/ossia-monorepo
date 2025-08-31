import uuid

from pydantic import BaseModel, computed_field, Field

from pulsola.sync.enum import PlaybackType, LoopType


class Permissions(BaseModel):
    skip: bool = True
    edit: bool = True


class CreateSession(BaseModel):
    playback_id: str = Field(examples=['track:Kzg082SnR16cgb2hNNB79Q'])
    loop_mode: LoopType = Field(examples=[LoopType.OFF])
    shuffle: bool = Field(examples=[False])
    permissions: Permissions = Field(default_factory=Permissions, examples=[Permissions()])

    @computed_field()  # type: ignore[prop-decorator]
    @property
    def playback_type(self) -> PlaybackType:
        return PlaybackType(self.playback_id.split(':')[0])

    @computed_field()  # type: ignore[prop-decorator]
    @property
    def playback_oid(self) -> str:
        return PlaybackType(self.playback_id.split(':')[1])


class ListenerInfo(BaseModel):
    oid: uuid.UUID = Field(exclude=True)
    anonymous: bool = Field(exclude=True)
    username: str | None = Field(exclude=True)

    @computed_field()
    @property
    def name(self) -> str:
        if self.anonymous:
            return f'Anonym_{self.oid.hex[:8]}'
        return self.username


class SessionInfo(BaseModel):
    oid: uuid.UUID = Field(alias='id')
    listeners: list[ListenerInfo]
