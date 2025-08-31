<script setup lang="ts">
import Menu from "~/components/ui/Menu.vue"
import CreatorDisplay from "~/components/common/CreatorDisplay.vue"
import {Plus} from "lucide-vue-next"
import type {ChannelItems} from "~/utils/types";
import type {CreatorInfo} from "~/schemas/creator";

const { creatorId } = useRoute().params;
const menuRef = useTemplateRef('menuRef')
const profile = useProfileStore()

const currentCreator = computed<CreatorInfo | undefined>(() => {
    return profile.creatorsMap.get(creatorId as string)
})

const creatorItems = computed(() => {
    if (profile.creators && profile.creators.length > 0) {
        const channelArray: ChannelItems = profile.creators.map(creator => {
            return {
                oid: creator.id,
                label: creator.display_name,
                avatar: creator.has_avatar,
                isCreatorLink: true,
                route: `/studio/${creator.url}`
            }
        })

        return channelArray
    }
    return [{
        label: 'Создать канал',
        _icon: Plus,
        route: '/studio'
    }]
})

const items = ref([
    {
      label: "Главная",
      route:  `/studio/${creatorId}`
    },
    {
      separator: true
    },
    {
        label: "Контент",
        items: [
            {
                label: "Композиции",
                route: `/studio/${creatorId}/library`
            }
        ]
    }
])

function toggle(event: MouseEvent) {
    menuRef.value!.toggle(event)
}
</script>

<template>
    <aside class="fixed top-0 bottom-0 left-0 pt-2 w-2xs bg-surface-100 dark:bg-surface-850 flex flex-col">
        <Menu :model="items" class="h-full pl-4 border-none" pt:root="bg-transparent dark:bg-transparent">
            <template #start>
                <NuxtLink to="/">
                    <NuxtImg src="/logo-full.png" height="64px"/>
                </NuxtLink>
            </template>
            <template #item="{ item }">
                <div class="flex items-center p-2 gap-2">
                    <NuxtLink :to="item.route" class="w-full flex items-center gap-2">
                        <component :is="item._icon"/>
                        <span>{{ item.label }}</span>
                    </NuxtLink>
                </div>
            </template>
        </Menu>
        <div class="bg-surface-0 dark:bg-surface-900 absolute w-full bottom-0">
            <CreatorDisplay
                v-if="currentCreator" :id="currentCreator.id" :display-name="currentCreator.display_name"
                :has-avatar="currentCreator.has_avatar"
                class="hover:cursor-pointer ml-4 mb-8 mt-4 mr-1 p-2 hover:bg-surface-100 dark:hover:bg-surface-800 group transition-colors duration-200 rounded-sm text-surface-700 dark:text-surface-0"
                @click="toggle"
            />
            <Menu ref="menuRef" :model="creatorItems" popup>
                <template #item="{ item }">
                    <div class="flex items-center p-2 gap-2">
                        <NuxtLink :to="item.route" class="w-full flex items-center gap-2">
                            <CreatorDisplay :id="item.oid" :display-name="item.label" :has-avatar="item.avatar"/>
                        </NuxtLink>
                    </div>
                </template>
            </Menu>
        </div>
    </aside>
</template>

<style scoped>

</style>