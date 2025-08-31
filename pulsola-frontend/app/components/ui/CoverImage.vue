<script setup lang="ts">
import {Disc3} from "lucide-vue-next"

withDefaults(defineProps<{
    src: string;
    disabled?: boolean;
    width?: number | string;
    height?: number | string;
}>(), {
    width: 256,
    height: 256,
})
</script>

<template>
    <NuxtImg v-if="!disabled" :src="src" :width="width" :height="height"/>
    <div v-else class="bg-surface-200 flex justify-center items-center">
        <Disc3/>
    </div>
</template>

<style scoped>

</style>