<template>
    <StepItem
        :pt="theme"
        :pt-options="{
            mergeProps: ptViewMerge
        }"
        unstyled
    >
        <slot/>
    </StepItem>
</template>

<script lang="ts" setup>
import StepItem, {type StepItemPassThroughOptions, type StepItemProps} from 'primevue/stepitem';
import {ref} from 'vue';
import {ptViewMerge} from '../utils';

defineProps</* @vue-ignore */ StepItemProps>();

const theme = ref<StepItemPassThroughOptions>({
    root: `flex flex-col flex-initial p-active:flex-auto last-of-type:*:last:ps-8`
});
</script>
