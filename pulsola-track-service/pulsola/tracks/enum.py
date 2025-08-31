import enum


class TrackStatus(enum.StrEnum):
    """
    Track uploading status enum used in database.
    Entries length must be 16 or fewer chars
    """

    QUEUED = 'queued'
    PROCESSING = 'processing'
    READY = 'ready'
    BLOCKED = 'blocked'
    ERROR = 'error'


class TrackVisibility(enum.StrEnum):
    """
    Track visibility enum used in database.
    Entries length must be 8 or fewer chars
    """

    DRAFT = 'draft'
    PUBLIC = 'public'
    LINK = 'link'
    PRIVATE = 'private'


class DownloadType(enum.StrEnum):
    ALL = 'all'
    SELECTED = 'selected'
