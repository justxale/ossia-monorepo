import uuid
from datetime import datetime
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    computed_field,
    model_validator,
)

from pulsola.tracks.datamodels.creators import CreatorInfo
from pulsola.tracks.enum import DownloadType, TrackStatus, TrackVisibility
from pulsola.tracks.services.encode import FFMpegEncoder


class TrackInfo(BaseModel):
    oid: uuid.UUID = Field(validation_alias='id', exclude=True)
    title: str = Field(min_length=1, max_length=32)
    description: str | None = Field(max_length=512)
    duration: int
    has_cover: bool
    visibility: TrackVisibility
    status: TrackStatus
    creator: CreatorInfo

    created_at: datetime

    @computed_field()  # type: ignore[prop-decorator]
    @property
    def id(self) -> str:
        return FFMpegEncoder.encode_track_id(self.oid)


class TracksResponse(BaseModel):
    tracks: list[TrackInfo]


class UpdateTrack(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: (
            list[
                Annotated[
                    str,
                    StringConstraints(
                        strip_whitespace=True, to_lower=True, pattern=r'^[a-z]+$'
                    ),
                ]
            ]
            | None
    ) = Field(None, max_length=32)

    visibility: TrackVisibility | None = None


class DownloadTracks(BaseModel):
    action: DownloadType
    track_ids: list[str] | None = None

    @model_validator(mode='after')
    def validate_action(self) -> Self:
        if self.action == DownloadType.SELECTED and self.track_ids is None:
            raise ValueError('IDs must be specified when downloading selected tracks')
        return self
