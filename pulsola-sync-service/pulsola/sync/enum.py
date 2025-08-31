import enum


class SessionAction(enum.StrEnum):
    PAUSE = 'pause'
    RESUME = 'resume'
    SEEK = 'seek'
    NEXT = 'next'
    PREVIOUS = 'previous'


class EventType(enum.StrEnum):
    SYNC = 'onsync'
    ACTION = 'onaction'
    ON_CONNECT = 'onconnect'
    ON_END = 'onplaybackend'


class PlaybackType(enum.StrEnum):
    PLAYLIST = 'playlist'
    TRACK = 'track'


class LoopType(enum.StrEnum):
    ONLY_PLAYBACK = 'playback'
    OFF = 'off'


class WebsocketStatus(enum.IntEnum):
    UNAUTHORIZED = 3000
    FORBIDDEN = 3003
    TIMEOUT = 3008
    OK = 4000
