import type {CreatorInfo} from "~/schemas/creator";
import type {UserProfile, UserCreators} from "~/schemas/profile";

export const useProfileStore = defineStore('profile', () => {
    const isAuthorized = ref<boolean>(false);
    const userId = ref<string | undefined>(undefined)
    const username = ref<string | undefined>(undefined)
    const displayName = ref<string | undefined>(undefined)
    const hasAvatar = ref(false)
    const creators = ref<CreatorInfo[] | undefined>(undefined)
    const creatorsMap = computed<Map<string, CreatorInfo>>(() => {
        const map = new Map()
        creators.value?.map((v) => {
            map.set(v.url, v)
        })
        return map
    })

    async function fetchProfile() {
        const {$api} = useNuxtApp()
        const token = useCookie('access_token')
        try {
            const res = await $api<UserProfile>('/me/', {
                headers: {
                    Authorization: `Bearer ${token.value}`
                },
                onResponseError(res) {
                    if (token.value && res.response.status === 401) {
                        navigateTo('/me/login')
                    }
                }
            })
            isAuthorized.value = true
            userId.value = res.id
            username.value = res.username
            displayName.value = res.display_name
            hasAvatar.value = res.has_avatar
        } catch {
            isAuthorized.value = false
            userId.value = undefined
            username.value = undefined
            displayName.value = undefined
            hasAvatar.value = false
        }
    }

    async function fetchCreators() {
        const {$api} = useNuxtApp()
        const token = useCookie('access_token')
        try {
            const res = await $api<UserCreators>('/creators/', {
                headers: {
                    Authorization: `Bearer ${token.value}`
                },
                onResponseError(res) {
                    if (token.value && res.response.status === 401) {
                        navigateTo('/me/login')
                    }
                }
            })
            creators.value = res.creators
        } catch {
            creators.value = undefined
        }
    }

    return {
        userId, username, displayName, hasAvatar, creators, isAuthorized, creatorsMap,
        fetchProfile, fetchCreators
    }
})