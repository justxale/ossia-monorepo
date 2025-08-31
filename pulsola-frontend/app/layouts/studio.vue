<script lang="ts" setup>
import StudioSidebar from "~/components/layout/StudioSidebar.vue"
import StudioHeader from "~/components/layout/StudioHeader.vue"

useHead({
    titleTemplate: title => title ? `${title} - Ossia.Studio` : 'Ossia.Studio'
})

async function fetchAll() {
    await Promise.all([store.fetchProfile(), store.fetchCreators()])
}

const store = useProfileStore()
await callOnce(fetchAll)

if (!store.isAuthorized) {
    await navigateTo('/me/login?err=expired')
}
</script>

<template>
    <div class="flex justify-center items-center w-full min-h-[100vh] bg-surface-200 dark:bg-surface-800">
        <StudioHeader/>
        <StudioSidebar/>
        <slot/>
    </div>
</template>

<style scoped>

</style>