<script setup lang="ts">
const props = withDefaults(defineProps<{
    throttle?: number,
    duration?: number,
    hideDelay?: number,
    resetDelay?: number,
    
    height?: number,
    color?: string,
    errorColor?: string,
    estimatedProgress?: (duration: number, elapsed: number) => number
}>(), {
    throttle: 200,
    duration: 2000,
    hideDelay: 500,
    resetDelay: 400,
    height: 3,
    color: 'repeating-linear-gradient(to right, var(--color-primary-300) 0%, var(--color-primary-100) 40%, var(--color-primary-200) 100%)',
    errorColor: 'repeating-linear-gradient(to right, var(--color-primary-300) 0%, var(--color-primary-100) 40%, var(--color-primary-200) 100%)',
    estimatedProgress: defaultProgress
})

const { progress, isLoading, error } = useLoadingIndicator({
    duration: props.duration,
    throttle: props.throttle,
    hideDelay: props.hideDelay,
    resetDelay: props.resetDelay,
    estimatedProgress: props.estimatedProgress
})
</script>

<script lang="ts">
function defaultProgress(duration: number, elapsed: number) {
    return (2 / Math.PI * 100) * Math.atan(elapsed / duration * 100 / 50)
}
</script>

<template>
    <div
        class="absolute right-0 left-0 top-[4rem] pointer-events-none w-auto origin-left duration-200 z-30" :style="{
            opacity: isLoading ? '100%' : '0%',
            background: error ? errorColor : color,
            backgroundSize: `${(100 / progress) * 100}% auto`,
            transform: `scaleX(${progress}%)`,
            height: `${height}px`,
            transition: 'transform 0.1s, height 0.4s, opacity 0.4s'
        }"
    />
</template>

<style scoped>

</style>