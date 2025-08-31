<template>
    <Fluid unstyled>
        <slot/>
    </Fluid>
</template>

<script lang="ts" setup>
import Fluid, {type FluidProps} from 'primevue/fluid';

defineProps</* @vue-ignore */ FluidProps>();
</script>
