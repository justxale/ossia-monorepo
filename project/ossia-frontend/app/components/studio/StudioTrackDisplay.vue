<script lang="ts" setup>
import {parseDuration} from "~/utils/int";
import Slider from '~/components/ui/Slider.vue'

const props = defineProps<{
    withThumbnail: boolean,
    title: string
    durationInSeconds: number
}>()
const currentPosition = ref<number>(0);

const parsedDuration = computed<string>(() => {
    const {hours, minutes, seconds} = parseDuration(props.durationInSeconds)
    if (hours >= 0) return [hours, minutes, seconds].join(':')
    return [minutes, seconds].join(':')
})

const parsedPosition = computed(() => {
    const {hours, minutes, seconds} = parseDuration(currentPosition.value)
    if (hours >= 0) return [hours, minutes, seconds].join(':')
    return [minutes, seconds].join(':')
})
</script>

<template>
    <div class="flex justify-between items-center pt-2">
        {{ title }}
        <div class="flex items-center">
            <button>play</button>
            <Slider :max="durationInSeconds" :min="0" class="w-[256px]" orientation="horizontal"/>
            <span>{{ parsedPosition }} / {{ parsedDuration }}</span>
        </div>
    </div>
</template>

<style scoped>

</style>