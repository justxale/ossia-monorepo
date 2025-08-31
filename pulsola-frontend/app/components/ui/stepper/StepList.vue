<template>
    <StepList
        :pt="theme"
        :pt-options="{
            mergeProps: ptViewMerge
        }"
        unstyled
    >
        <slot/>
    </StepList>
</template>

<script lang="ts" setup>
import StepList, {type StepListPassThroughOptions, type StepListProps} from 'primevue/steplist';
import {ref} from 'vue';
import {ptViewMerge} from '../utils';

defineProps</* @vue-ignore */ StepListProps>();

const theme = ref<StepListPassThroughOptions>({
    root: `relative flex justify-between items-center m-0 p-0 list-none overflow-x-auto`
});
</script>
