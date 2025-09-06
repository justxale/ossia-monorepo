<script async lang="ts" setup>
import type {CreatorInfo, CreatorTracks} from "~/schemas/creator"
import TrackDisplay from "~/components/common/TrackDisplay.vue"
import Avatar from "~/components/ui/Avatar.vue"
import DataView from "~/components/ui/DataView.vue"

const {creatorId} = useRoute().params

const {data: creatorData} = await useAPI<CreatorInfo>(`/creators/${creatorId}/`)
const {data: trackData} = await useAPI<CreatorTracks>(`/creators/${creatorId}/tracks/`)

const endpoint = useAppConfig().apiEndpoint
</script>

<template>
    <div>
        <div>
            <div class="flex">
                <div>
                    <Avatar v-if="creatorData?.has_avatar" :image="`${endpoint}/creator/${creatorData?.id}/avatar`"/>
                    <Avatar v-else :label="creatorData?.display_name.charAt(0).toUpperCase()"/>
                </div>
                <div>{{ creatorData?.display_name }}</div>
            </div>
        </div>
        <DataView v-if="trackData" :value="trackData?.tracks">
            <template #list="slotProps">
                <div class="flex flex-col">
                    <TrackDisplay
                        v-for="(track, index) in slotProps.items" :key="index"
                        :created-at="track.created_at" :duration="track.duration" :oid="track.id"
                        :title="track.title"
                    />
                </div>
            </template>
        </DataView>
    </div>
</template>

<style scoped>

</style>