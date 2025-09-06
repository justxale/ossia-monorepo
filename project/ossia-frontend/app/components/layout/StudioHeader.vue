<script lang="ts" setup>
import {Moon, Sun, Upload} from "lucide-vue-next"
import LoadingBar from "~/components/layout/LoadingBar.vue"
import UploadStepper from "~/components/dialog/UploadStepper.vue"
import ProfileMenu from "~/components/layout/ProfileHeaderMenu.vue"

const profile = useProfileStore()
const colorMode = useColorMode()

const isDialogVisible = ref<boolean>(false)

function switchColorMode(to: string) {
    colorMode.preference = to
}
</script>

<template>
    <header class="absolute top-0 left-0 right-0 z-0 flex items-center justify-end px-4 h-16 bg-surface-100 dark:bg-surface-850">
        <div class="flex items-center gap-4">
            <div v-if="profile.isAuthorized">
                <Upload class="dark:text-surface-0 cursor-pointer" @click="isDialogVisible = true"/>
                <UploadStepper v-model:visible="isDialogVisible"/>
            </div>
            <div>
                <Moon v-if="colorMode.unknown" class="dark:text-surface-0"/>
                <Sun v-if="colorMode.value === 'light'" class="dark:text-surface-0 cursor-pointer" @click="() => switchColorMode('dark')"/>
                <Moon v-else-if="colorMode.value === 'dark'" class="dark:text-surface-0 cursor-pointer" @click="() => switchColorMode('light')"/>
            </div>
            <ProfileMenu v-if="profile.isAuthorized"/>
            <div v-else>
                <NuxtLink class="text-surface-700 dark:text-surface-0" to="/me/login">Войти</NuxtLink>
            </div>
        </div>
        <LoadingBar/>
    </header>
</template>