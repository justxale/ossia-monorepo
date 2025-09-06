<script lang="ts" setup>
import AppHeader from "~/components/layout/AppHeader.vue";

const store = useProfileStore()
useHead({
    titleTemplate: title => title ? `${title} - Ossia` : 'Ossia'
})
await callOnce(async () => Promise.all([store.fetchProfile(), store.fetchCreators()]))
</script>

<template>
    <div class="flex justify-center items-center w-full min-h-[100vh]">
        <AppHeader/>
        <slot/>
    </div>
</template>

<style scoped>

</style>