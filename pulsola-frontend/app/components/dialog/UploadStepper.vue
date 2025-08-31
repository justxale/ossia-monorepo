<script lang="ts" setup>
import Dialog from "~/components/ui/Dialog.vue"
import Button from "~/components/ui/Button.vue"
import SecondaryButton from "~/components/ui/SecondaryButton.vue"
import Stepper from '~/components/ui/stepper/Stepper.vue'
import StepList from '~/components/ui/stepper/StepList.vue'
import Step from '~/components/ui/stepper/Step.vue'
import StepPanels from '~/components/ui/stepper/StepPanels.vue'
import StepPanel from '~/components/ui/stepper/StepPanel.vue'
import InputTrack from "~/components/ui/forms/InputTrack.vue"
import InputText from "~/components/ui/forms/InputText.vue"
import TextArea from "~/components/ui/forms/TextArea.vue"
import Message from "~/components/ui/Message.vue"
import Select from "~/components/ui/Select.vue"

import {Form, FormField, type FormFieldState, /*type FormSubmitEvent*/} from "@primevue/forms"
import {zodResolver} from "@primevue/forms/resolvers/zod"
import * as zod from 'zod'
import CreatorDisplay from "~/components/common/CreatorDisplay.vue";
import type {CreatorInfo} from "~/schemas/creator";

const isFilePresent = ref<boolean>(false)
//const uploadingProcess = ref<number>(0)
const profile = useProfileStore()
const creatorOptions = computed(() => profile.creators?.map((v: CreatorInfo) => {
    return {
        displayName: v.display_name,
        hasAvatar: v.has_avatar,
        id: v.id
    }
}))

const resolver = zodResolver(zod.object({
    title: zod.string().max(32).optional(),
    description: zod.string().max(4096).optional(),
    track: zod.custom<File>().nonoptional()
}))

const visible = defineModel<boolean>('visible', {default: false})

/*async function sendBlob(ev: FormSubmitEvent) {
    const config = useAppConfig()
    const data = new FormData()
    data.set('title', ev.values.title)
    data.set('description', ev.values.description)
    data.set('track', ev.values.track)

    const req = new XMLHttpRequest()
    req.open('POST', config.baseURL + config.apiEndpoint, true)
    req.setRequestHeader('Accept', 'application/json; charset=utf-8')
    req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded')
    req.onprogress = (progress) => {
        uploadingProcess.value = progress.loaded / progress.total
    }
    req.send(data)
}*/

function onClick(value: string, formState: { [p: string]: FormFieldState }, cb: (v: string) => void) {
    switch (value) {
        case '1':
            if (formState.track?.valid) {
                cb('2')
            }
            break
        case '2':
            cb('3')
            break
    }
}

function onUpload() {

}
</script>

<template>
    <Dialog v-model:visible="visible" :closable="false" class="basis-[50rem] w-[50rem]" modal>
        <Stepper linear value="0">
            <StepList>
                <Step value="0">Автор</Step>
                <Step value="1">Загрузка</Step>
                <Step value="2">Информация</Step>
                <Step value="3">Публикация</Step>
            </StepList>

            <StepPanels>
                <Form v-slot="$form" :resolver @submit="onUpload">
                    <StepPanel v-slot="{activateCallback}" value="0">
                        <Select :options="creatorOptions" placeholder="Выберите канал" option-label="displayName">
                            <template #value="slotProps">
                                <CreatorDisplay v-if="slotProps.value" :id="slotProps.value.id" :display-name="slotProps.value.displayName" :has-avatar="slotProps.value.hasAvatar"/>
                                <span v-else>{{ slotProps.placeholder }}</span>
                            </template>
                            <template #header>
                                <div class="p-3 font-bold">Ваши авторы</div>
                            </template>
                            <template #empty>
                                У вас нет каналов
                            </template>
                            <template #option="slotProps">
                                <div class="flex items-center">
                                    <CreatorDisplay :id="slotProps.option.id" :display-name="slotProps.option.displayName" :has-avatar="slotProps.option.hasAvatar"/>
                                </div>
                            </template>
                            <template #footer>
                                <div class="p-3 w-full dark:hover:bg-surface-700 hover:bg-surface-200">
                                    <NuxtLink to="/studio" class="block" @click="visible = false">Создать канал</NuxtLink>
                                </div>
                            </template>

                        </Select>
                        <div class="flex pt-6 justify-between">
                            <SecondaryButton label="Отмена" @click="visible = false"/>
                            <Button
                                :disabled="!isFilePresent" label="Далее"
                                @click="onClick('0', $form, () => activateCallback('1'))"
                            />
                        </div>
                    </StepPanel>
                    <StepPanel v-slot="{activateCallback}" value="1">
                        <FormField name="track">
                            <InputTrack v-model:is-file-present="isFilePresent"/>
                            <Message v-if="$form.track?.invalid" severity="error">Загрузите файл</Message>
                        </FormField>
                        <div class="flex pt-6 justify-between">
                            <SecondaryButton label="Назад" @click="activateCallback('0')"/>
                            <Button
                                :disabled="!isFilePresent" label="Далее"
                                @click="onClick('1', $form, () => activateCallback('2'))"
                            />
                        </div>
                    </StepPanel>
                    <StepPanel v-slot="{activateCallback}" value="2">
                        <div>
                            <InputText name="title"/>
                            <TextArea name="description"/>
                        </div>
                        <div class="flex pt-6 justify-between">
                            <SecondaryButton label="Назад" @click="activateCallback('1')"/>
                            <Button
                                icon-pos="right" label="Далее"
                                @click="onClick('2', $form, () => activateCallback('3'))"
                            />
                        </div>
                    </StepPanel>
                    <StepPanel v-slot="{activateCallback}" value="3">
                        <div class="flex pt-6 justify-between">
                            <SecondaryButton label="Назад" @click="activateCallback('2')"/>
                            <Button icon-pos="right" label="Готово" type="submit"/>
                        </div>
                    </StepPanel>
                </Form>
            </StepPanels>
        </Stepper>
    </Dialog>
</template>

<style scoped>

</style>