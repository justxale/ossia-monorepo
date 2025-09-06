type Item = {
    label: string
    _icon?: unknown
    route?: string
}
export type ChannelItems = (Item & {
    oid?: string
    avatar?: boolean
    isCreatorLink?: boolean
    items?: Item[]
})[]