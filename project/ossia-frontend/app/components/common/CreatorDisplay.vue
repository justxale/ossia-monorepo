<script setup lang="ts">
import Avatar from "~/components/ui/Avatar.vue";

defineProps<{
    id: string
    displayName: string
    hasAvatar?: boolean
}>()
</script>

<template>
    <div class="flex items-center gap-2">
        <Avatar v-if="hasAvatar" src="" shape="circle" />
        <Avatar v-else :label="displayName.charAt(0).toUpperCase()" shape="circle"/>
        <span>{{ displayName }}</span>
    </div>

</template>

<style scoped>

</style>