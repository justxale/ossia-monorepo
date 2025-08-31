<script setup lang="ts">
import CreatorDisplay from "~/components/common/CreatorDisplay.vue"
import Avatar from "~/components/ui/Avatar.vue"
import Menu from '~/components/ui/Menu.vue'

import {LogOut, Plus, Settings} from "lucide-vue-next"
import type {ChannelItems} from "~/utils/types";

const menuRef = useTemplateRef<typeof Menu>('menuRef')
const profile = useProfileStore()

const creatorsItem = computed(() => {
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
        channelArray.push({
            label: 'Создать канал',
            _icon: Plus,
            route: '/studio'
        })

        return channelArray
    }
    return [{
        label: 'Создать канал',
        _icon: Plus,
        route: '/studio'
    }]
})

const menuItems = computed(() => {
    const required = [{
        label: "Профиль",
        items: [
            {
                label: "Настройки",
                _icon: Settings
            },
            {
                label: "Выйти из аккаунта",
                _icon: LogOut
            }
        ]
    }]

    if (creatorsItem.value.length > 0) {
        return [{
            label: "Каналы",
            items: creatorsItem.value
        }].concat(required)
    }
    return required
})

function toggle(event: Event) {
    menuRef.value!.toggle(event)
}
</script>

<template>
    <div>
        <Menu ref="menuRef" :model="menuItems" popup>
            <template #item="{ item }">
                <div class="flex items-center p-2 gap-2">
                    <template v-if="item.isCreatorLink">
                        <NuxtLink :to="item.route" class="w-full flex items-center gap-2">
                            <CreatorDisplay :id="item.oid" :display-name="item.label" :has-avatar="item.avatar"/>
                        </NuxtLink>
                    </template>

                    <template v-else>
                        <NuxtLink :to="item.route" class="w-full flex items-center gap-2">
                            <component :is="item._icon"/>
                            <span>{{ item.label }}</span>
                        </NuxtLink>
                    </template>
                </div>
            </template>
        </Menu>
        <div class="dark:text-surface-0 cursor-pointer" @click="toggle">
            <span class="pr-2">{{ profile.displayName }}</span>
            <Avatar v-if="profile.hasAvatar" src="/me/avatar" shape="circle"/>
            <Avatar v-else :label="profile.displayName!.charAt(0).toUpperCase()" shape="circle"/>
        </div>
    </div>
</template>