<template>
    <StepPanels
        :pt="theme"
        :pt-options="{
            mergeProps: ptViewMerge
        }"
        unstyled
    >
        <slot/>
    </StepPanels>
</template>

<script lang="ts" setup>
import StepPanels, {type StepPanelsPassThroughOptions, type StepPanelsProps} from 'primevue/steppanels';
import {ref} from 'vue';
import {ptViewMerge} from '../utils';

defineProps</* @vue-ignore */ StepPanelsProps>();

const theme = ref<StepPanelsPassThroughOptions>({
    root: `pt-[0.875rem] pb-[1.125rem] px-2`
});
</script>
