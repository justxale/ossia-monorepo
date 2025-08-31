<script lang="ts" setup>
import {Form, FormField, type FormSubmitEvent} from "@primevue/forms"
import InputText from "~/components/ui/forms/InputText.vue"
import Password from "~/components/ui/forms/Password.vue"
import Button from "~/components/ui/Button.vue"
import Message from '~/components/ui/Message.vue'
import Card from "~/components/ui/Card.vue"
import {zodResolver} from "@primevue/forms/resolvers/zod"
import * as zod from 'zod'

definePageMeta({
    layout: 'empty'
})

const resolver = zodResolver(
    zod.object({
        display_name: zod.string(
            {
                error: "Обязательное поле"
            })
            .max(64, {error: "Публичное имя должно быть короче 64 символов"}),
        password: zod.string({error: "Обязательное поле"})
            .min(8, {
                error: 'Пароль не должен быть короче 8 символов'
            })
            .regex(
                /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^+=_()-])[A-Za-z\d@$!%*?&#^+=_()-]{8,}$/, {
                    error: "Пароль должен включать как минимум одну заглавную и одну строчную Латинскую букву, как минимум одну цифру и один специальный символ"
                }),
        confirmPassword: zod.string({error: "Обязательное поле"})
    }).refine((values) => {
        const res = values.password === values.confirmPassword
        passwordMismatch.value = !res
        return res
    }, {error: "Пароли должны совпадать"})
)
const usernameResolver = zodResolver(
    zod.string({error: "Обязательное поле"})
        .min(
            4, {
                error: "Имя пользователя должно быть длиннее 4 и короче 32 символов",
                abort: true
            }
        )
        .max(
            32, {
                error: "Имя пользователя должно быть длиннее 4 и короче 32 символов",
                abort: true
            }
        ).regex(
        /^[a-zA-Z0-9_-]+$/, {
            error: "Имя пользователя может состоять только из заглавных и строчных букв латиницы, цифр и символов _ и -",
            abort: true
        }
    )
        .refine(async (val) => {
            const {$api} = useNuxtApp()
            try {
                await $api(`/oauth/register?u=${val}`, {
                    method: "GET"
                })
                return true
            } catch {
                return false
            }
        }, {error: "Имя пользователя уже занято"})
)

let timeoutId: unknown;

function resolve(values: unknown) {
    clearTimeout(timeoutId as number)
    return new Promise(res => {
        timeoutId = setTimeout(async () => {
            res(await usernameResolver(values))
        }, 500)
    })
}

const isError = ref<boolean>(false)
const passwordMismatch = ref<boolean>(false)

const {$api} = useNuxtApp()
const profile = useProfileStore()

async function onFormSubmit(event: FormSubmitEvent) {
    isError.value = false
    if (!event.valid) return

    try {
        await $api(`/oauth/register`, {
            method: "POST",
            body: JSON.stringify({
                username: event.values.username,
                password: event.values.password,
                display_name: event.values.display_name
            }),
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
    <Card class="min-w-80 max-w-md w-[20vw] max-h-[40vh]">
        <template #header>
            <div class="flex justify-center mt-3">
                <NuxtImg src="/logo-full.png" width="192px"/>
            </div>
        </template>
        <template #content>
            <div>
                <Form :resolver class="flex flex-col gap-4" @submit="onFormSubmit">
                    <FormField v-slot="$field" :resolver="resolve" name="username">
                        <InputText class="pb-1" fluid placeholder="Имя пользователя" required/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                    </FormField>
                    <FormField v-slot="$field" name="display_name">
                        <InputText class="pb-1" fluid placeholder="Публичное имя пользователя" required/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                    </FormField>
                    <FormField v-slot="$field" name="password">
                        <Password class="pb-1" :feedback="false" fluid placeholder="Пароль" toggle-mask required/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                    </FormField>
                    <FormField v-slot="$field" name="confirmPassword">
                        <Password class="pb-1" :feedback="false" fluid placeholder="Подтвердите пароль" required/>
                        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                            {{ $field.error?.message }}
                        </Message>
                        <Message v-if="passwordMismatch" severity="error" size="small" variant="simple">
                            Проверьте, чтобы пароли совпадали
                        </Message>
                    </FormField>
                    <Message v-if="isError" severity="error" size="small" variant="simple">
                        Что-то пошло не так, попробуйте попытку позже
                    </Message>
                    <Button label="Зарегистрироваться" severity="secondary" type="submit"/>
                    <NuxtLink class="text-center text-primary-300 hover:text-primary-200" to="/me/login">
                        Уже есть аккаунт? Войти
                    </NuxtLink>
                </Form>
            </div>
        </template>
    </Card>

</template>

<style scoped>

</style>