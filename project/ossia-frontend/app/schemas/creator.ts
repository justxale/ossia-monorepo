export type CreatorInfo = {
    id: string
    url: string
    display_name: string
    description?: string
    tags?: string[]

    has_avatar?: boolean
    has_banner?: boolean
}

enum TrackVisibility {
    DRAFT = 'draft',
    PUBLIC = 'public',
    LINK = 'link',
    PRIVATE = 'private',
}

enum TrackStatus {
    QUEUED = 'queued',
    PROCESSING = 'processing',
    READY = 'ready',
    BLOCKED = 'blocked',
    ERROR = 'error'
}

export type TrackInfo = {
    id: string
    title: string
    description?: string
    duration: number
    has_cover: boolean
    visibility: TrackVisibility
    status: TrackStatus
    creator?: CreatorInfo

    created_at: string
}

export type CreatorTracks = {
    tracks: TrackInfo[],
}
