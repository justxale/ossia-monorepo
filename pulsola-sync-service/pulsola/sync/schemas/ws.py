from typing import Literal, Union

from pydantic import BaseModel, Field

from pulsola.sync.enum import SessionAction, EventType


class SyncEvent(BaseModel):
    event_type: Literal[EventType.SYNC] = EventType.SYNC
    elapsed: float | None = None


class ActionEvent(BaseModel):
    event_type: Literal[EventType.ACTION] = EventType.ACTION
    action: SessionAction


class OnConnectEvent(BaseModel):
    event_type: Literal[EventType.ON_CONNECT] = EventType.ON_CONNECT
    token: str | None = None
    client_id: str | None = None
    current_position: float | None = None


class OnEndEvent(BaseModel):
    event_type: Literal[EventType.ON_END] = EventType.ON_END


type Event = Union[SyncEvent, ActionEvent, OnConnectEvent, OnEndEvent]


class WebsocketMessage(BaseModel):
    event: Event = Field(discriminator='event_type')
    client_id: str | None = None


class WebsocketResponse(BaseModel):
    code: int
    event: Event


class WebsocketError(BaseModel):
    code: int
    msg: str | None = None
