<script lang="ts" setup>
import WaveSurfer from "wavesurfer.js"
import Skeleton from "~/components/ui/Skeleton.vue"

const props = defineProps<{
    blob: Blob,
}>()
const isLoaded = ref<boolean>(false)
const containerRef = useTemplateRef<HTMLDivElement>('containerRef')

const isValid = defineModel<boolean>('isValid', {default: false})

onMounted(async () => {
    const surfer = WaveSurfer.create({
        container: containerRef.value!,
        waveColor: "#000000",
        barWidth: 4,
        barHeight: 0.5,
        barGap: 2,
        barRadius: 4,
    })
    try {
        await surfer.loadBlob(props.blob)
        isLoaded.value = true
        isValid.value = true
    } catch {
        isLoaded.value = false
    }
})

</script>

<template>
    <div ref="containerRef" class="h-32 w-[1024px]">
        <Skeleton v-if="!isLoaded" class="h-32 w-full"/>
    </div>
</template>

<style scoped>

</style>