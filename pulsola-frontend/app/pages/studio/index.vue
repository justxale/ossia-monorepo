<script setup lang="ts">
import {Form, FormField, type FormSubmitEvent} from "@primevue/forms"
import {X} from "lucide-vue-next"
import {zodResolver} from "@primevue/forms/resolvers/zod"
import * as zod from "zod"
import Message from "~/components/ui/Message.vue"
import InputText from "~/components/ui/forms/InputText.vue"
import TextArea from "~/components/ui/forms/TextArea.vue"
import Chip from "~/components/ui/Chip.vue"
import Card from "~/components/ui/Card.vue"
import Button from "~/components/ui/Button.vue"

const resolver = zodResolver(zod.object({
    displayName: zod.string().max(32, {error: "Имя автора должно быть короче 32 символов"}),
    url: zod.string().min(4).max(32).regex(/^[a-zA-Z0-9_-]+$/).optional(),
    description: zod.string().max(2**11).optional()
}))
const tagsArray = ref<Set<string>>(new Set<string>())
const tagInput = ref<string | undefined>(undefined)

const profile = useProfileStore()
const {$api} = useNuxtApp()
const isError = ref<boolean>(false)

function splitTags(value: string | undefined, force?: boolean) {
    if (!value) return
    if (force) {
        tagsArray.value.add(value.trim())
        tagInput.value = ''
    }

    const split = value.split(/[, ]/)
    if (split.length > 1 && split[0]) {
        tagsArray.value.add(split[0])
        tagInput.value = ''
    }
}

watch(tagInput, (value: string | undefined) => {
    splitTags(value)
})

function remCb(tag: string) {
    tagsArray.value.delete(tag)
}

function enterCb(event: KeyboardEvent) {
    if (event.key === "Enter") {
        splitTags(tagInput.value, true)
    }
}

async function onFormSubmit(event: FormSubmitEvent) {
    isError.value = false
    if (!event.valid) return

    try {
        await $api(`/creators/`, {
            method: "POST",
            body: JSON.stringify({
                display_name: event.values.displayName,
                url: event.values.url,
                description: event.values.description,
                tags: Array.from(tagsArray.value)
            }),
            async onResponseError(res) {
                if (res.response.status === 401) {
                    await navigateTo('/me/login')
                }
            }
        })
        await profile.fetchCreators()
        await navigateTo('/', {redirectCode: 302})

    } catch (e) {
        console.error(e)
        isError.value = true
    }
}
</script>

<template>
    <Card class="min-w-md max-w-2xl w-[25vw]">
        <template #header>
            <div class="text-center font-bold text-xl">
                <div class="flex justify-center mt-3">
                    <NuxtImg src="/logo-full.png" width="192px"/>
                </div>
                Создание автора
            </div>
        </template>
        <template #content>
            <div>
                <Form :resolver class="flex flex-col gap-4" @submit="onFormSubmit">
                    <FormField v-slot="$field" name="displayName">
                        <InputText class="pb-1" fluid placeholder="Публичное имя автора" required>
                            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                                {{ $field.error?.message }}
                            </Message>
                        </inputtext></FormField>
                    <FormField v-slot="$field" name="url">
                        <InputText class="pb-1" fluid placeholder="Публичная ссылка автора"/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                    </FormField>
                    <FormField v-slot="$field" name="description">
                        <TextArea class="pb-1 resize-none overflow-hidden" fluid placeholder="Описание" toggle-mask auto-resize/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                    </FormField>
                    <span class="text-surface-200 placeholder:text-surface-100">Тэги автора</span>
                    <div class="flex flex-wrap gap-4 bg-surface-0 dark:bg-surface-950 border border-surface-300 dark:border-surface-700 p-3">
                        <Chip v-for="(tag, i) in tagsArray" :key="i" :label="tag" removable>
                            <template #removeicon>
                                <X class="hover:cursor-pointer h-4" @click="() => remCb(tag)"/>
                            </template>
                        </Chip>
                        <InputText v-model="tagInput" class="pb-1" fluid @keydown="enterCb" @blur="() => splitTags(tagInput, true)"/>
                    </div>
                    <Message v-if="isError" severity="error" size="small" variant="simple">
                        Что-то пошло не так, попробуйте попытку позже
                    </Message>
                    <Button label="Создать автора" severity="secondary" type="submit"/>
                </Form>
            </div>
        </template>
    </Card>

</template>

<style scoped>

</style>