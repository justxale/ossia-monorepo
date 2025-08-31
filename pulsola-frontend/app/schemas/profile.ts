import type {CreatorInfo} from '~/schemas/creator' 

export type UserProfile = {
    id: string,
    username: string,
    display_name: string,
    has_avatar: boolean,
}

export type UserCreators = {
    creators: CreatorInfo[]
}