<script lang="ts" setup>
import {Form, FormField, type FormSubmitEvent} from "@primevue/forms"
import InputText from "~/components/ui/forms/InputText.vue"
import Password from "~/components/ui/forms/Password.vue"
import Button from "~/components/ui/Button.vue"
import Message from '~/components/ui/Message.vue'
import Card from "~/components/ui/Card.vue"
import {zodResolver} from "@primevue/forms/resolvers/zod"
import * as zod from 'zod'
import {useToast} from "primevue";

definePageMeta({
    layout: 'empty'
})

const { err } = useRoute().query

const resolver = zodResolver(
    zod.object({
        username: zod.string({error: "Введите имя пользователя"})
            .max(
                32, {
                    error: "Имя пользователя должно быть короче 32 символов",
                    abort: true
                }
            ).regex(
                /^[a-zA-Z0-9_-]+$/, {
                    error: "Имя пользователя может состоять только из заглавных и строчных букв латиницы, цифр и символов _ и -",
                    abort: true
                }
            ),
        password: zod.string({error: "Введите пароль"})
    })
)

const isError = ref<boolean>(false)
const {$api} = useNuxtApp()
const profile = useProfileStore()
const toast = useToast()

onMounted(() => {
    if (err) {
        toast.add({
            severity: 'error',
            summary: "Ошибка авторизации",
            detail: "Текущая сессия истекла, войдите снова",
            life: 5000,
        })
    }
})

async function onFormSubmit(event: FormSubmitEvent) {
    isError.value = false
    if (!event.valid) return

    const form = new FormData()
    form.append("username", event.values.username)
    form.append("password", event.values.password)
    try {
        await $api(`/oauth/token`, {
            method: "POST",
            // @ts-expect-error IDK what is going on here, form is working correctly in browser
            body: new URLSearchParams(form).toString(),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            credentials: 'include'
        })
        await Promise.all([
            profile.fetchProfile(), profile.fetchCreators()
        ])
        await navigateTo('/', {redirectCode: 302})
    } catch (e) {
        console.error(e)
        isError.value = true
    }
}
</script>

<template>
    <Card class="min-w-80 max-w-md w-[20vw] max-h-[35vh]">
        <template #header>
            <div class="flex justify-center mt-3">
                <NuxtImg src="/logo-full.png" width="192px"/>
            </div>
        </template>
        <template #content>
            <div>
                <Form :resolver class="flex flex-col gap-4" @submit="onFormSubmit">
                    <FormField v-slot="$field" name="username">
                        <InputText class="pb-1" fluid placeholder="Имя пользователя" required/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                    </FormField>
                    <FormField v-slot="$field" name="password">
                        <Password :feedback="false" class="pb-1" fluid placeholder="Пароль" toggle-mask required/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                    </FormField>
                    <Message v-if="isError" severity="error" size="small" variant="simple">
                        Что-то пошло не так, проверьте введённые данные или попробуйте позже
                    </Message>
                    <Button label="Войти" severity="secondary" type="submit"/>
                    <NuxtLink class="text-center text-primary-300 hover:text-primary-200" to="/me/register">
                        Ещё нет аккаунта? Зарегистрироваться
                    </NuxtLink>
                </Form>
            </div>
        </template>
    </Card>

</template>

<style scoped>

</style>