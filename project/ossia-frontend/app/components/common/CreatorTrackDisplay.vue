<script lang="ts" setup>
import type {CreatorInfo} from "~/schemas/creator"
// import Badge from "~/components/ui/Badge"
import {Download, Heart, Pause, Play, Share} from "lucide-vue-next"
import CoverImage from "~/components/ui/CoverImage.vue";

const props = defineProps<{
    oid: string
    title: string
    duration: number
    createdAt: string
    hasCover?: boolean

    creator?: CreatorInfo
}>()
const player = usePlayer()
const config = useAppConfig()
const endpoint = `${config.baseURL}${config.apiEndpoint}/tracks/${props.oid}/cover`

function playTrack() {
    player.currentTrack.value = props.oid

}
</script>

<template>
    <div class="group overflow-hidden transition-all hover:shadow-lg">
        <template #content>
            <div class="relative aspect-square overflow-hidden">
                <CoverImage :src="endpoint" :disabled="!hasCover" class="object-cover"/>

                <div
                    class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                >
                    <Button
                        class="w-16 h-16 rounded-full bg-white/90 text-black hover:bg-white hover:scale-110 transition-all"
                        size="lg"
                        @click="playTrack"
                    >
                        <Pause v-if="player.currentTrack.value === oid" class="w-6 h-6"/>
                        <Play v-else class="w-6 h-6 ml-1"/>
                    </Button>
                </div>

                <!--div class="absolute top-2 left-2">
                    <Badge class="bg-black/70 text-white border-none" variant="secondary">
                        {track.genre}
                    </Badge>
                </div-->
            </div>

            <div class="p-4">
                <div class="mb-2">
                    <h3 class="truncate">
                        {{ title }}
                    </h3>
                </div>

                <div class="flex items-center justify-between text-sm text-muted-foreground mb-3">
                    <span>{{ duration }}</span>
                    <span>{{ title }}</span>
                    <!--span>{track.plays.toLocaleString()} plays</span-->
                </div>

                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-1">
                        <Button class="p-1" size="sm" variant="ghost">
                            <Heart class="w-4 h-4"/>
                        </Button>
                        <!--span class="text-sm text-muted-foreground">{track.likes}</span-->
                    </div>
                    <div class="flex items-center space-x-1">
                        <Button class="p-1" size="sm" variant="ghost">
                            <Share class="w-4 h-4"/>
                        </Button>
                        <Button class="p-1" size="sm" variant="ghost">
                            <Download class="w-4 h-4"/>
                        </Button>
                    </div>
                </div>

                <div class="mt-2 pt-2 border-t border-border">
                    <p class="text-xs text-muted-foreground truncate">
                        {track.channelName}
                    </p>
                </div>
            </div>
        </template>
    </div>
</template>

<style scoped>

</style>