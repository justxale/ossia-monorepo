<script lang="ts" setup>
import WaveDisplay from "~/components/common/WaveDisplay.vue"

const fileModel = ref<File | undefined>(undefined)
const isFilePresent = defineModel<boolean>('isFilePresent', {default: false})

function onChange(e: Event) {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return
    fileModel.value = file
}
</script>

<template>
    <div>
        <div class="flex items-center gap-2">
            <label class="cursor-pointer p-3" for="track-input">Choose file</label>
            <input
                id="track-input" accept="audio/wav, audio/flac" class="hidden"
                type="file" @change="onChange"
            >
            <div v-if="fileModel">{{ fileModel.name }}</div>
            <div v-else>No file chosen</div>
        </div>
        <WaveDisplay v-if="fileModel" v-model:is-valid="isFilePresent" :blob="fileModel" class="w-full"/>
    </div>
</template>

<style scoped>

</style>