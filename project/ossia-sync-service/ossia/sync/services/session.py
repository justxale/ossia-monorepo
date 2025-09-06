import time
import uuid
from dataclasses import dataclass, field

from starlette.websockets import WebSocket

from ossia.sync.dependencies.security import User
from ossia.sync.enum import PlaybackType


@dataclass
class ListenerState:
    anonymous: bool
    socket: WebSocket
    username: str | None = None
    user_id: uuid.UUID | None = None
    oid: uuid.UUID = field(default_factory=uuid.uuid4)

    @property
    def encoded_id(self) -> str:
        return self.oid.hex


@dataclass
class SessionState:
    editable: bool
    skippable: bool

    playback_type: PlaybackType
    playback_id: str

    paused_at: float | None = None
    started_at: float = field(default_factory=lambda: time.time() + 1)
    is_paused: bool = False

    oid: uuid.UUID = field(default_factory=uuid.uuid4)
    listeners: dict[str, ListenerState] = field(default_factory=dict)

    @property
    def encoded_id(self) -> str:
        return self.oid.hex


class SessionService:
    _sessions: dict[str, SessionState] = {}

    def __init__(self, session: SessionState):
        self.session = session

    def attach_client(self, user: User | None, ws: WebSocket, ) -> ListenerState:
        _id = uuid.uuid4()
        if user:
            state = ListenerState(anonymous=False, socket=ws, user_id=user.oid, username=user.username)
        else:
            state = ListenerState(anonymous=True, socket=ws)
        self.session.listeners[_id.hex] = state
        return state

    def detach_client(self, client_id: str):
        pass

    def get_client_state(self, client_id: str):
        return self.session.listeners[client_id]

    @classmethod
    def get_session(cls, session_id: str):
        return cls._sessions[session_id]

    @classmethod
    def create_session(
            cls, editable: bool, skippable: bool,
            playback_type: PlaybackType, playback_id: str
    ):
        new_state = SessionState(editable, skippable, playback_type, playback_id)
        cls._sessions[new_state.encoded_id] = new_state
        return new_state
