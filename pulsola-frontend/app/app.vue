<script lang="ts" setup>
import './assets/css/tailwind.css'
import Toast from "~/components/ui/Toast.vue"
</script>

<template>
    <div class="min-h-[100vh] w-full">
        <Toast/>
        <NuxtRouteAnnouncer/>
        <NuxtLayout>
            <NuxtPage/>
        </NuxtLayout>
    </div>
</template>
