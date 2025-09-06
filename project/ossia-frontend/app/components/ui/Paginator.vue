<template>
    <Paginator
        :pt="theme"
        :pt-options="{
            mergeProps: ptViewMerge
        }"
        unstyled
    >
        <template
            #container="{ page, pageCount, pageLinks, changePageCallback, firstPageCallback, lastPageCallback, prevPageCallback, nextPageCallback }">
            <div class="flex flex-wrap gap-2 items-center justify-center">
                <SecondaryButton :disabled="page === 0" rounded text @click="firstPageCallback">
                    <template #icon>
                        <AngleDoubleLeftIcon/>
                    </template>
                </SecondaryButton>
                <SecondaryButton :disabled="page === 0" rounded text @click="prevPageCallback">
                    <template #icon>
                        <AngleLeftIcon/>
                    </template>
                </SecondaryButton>
                <div class="items-center justify-center gap-2 hidden sm:flex">
                    <SecondaryButton
                        v-for="pageLink of pageLinks" :key="pageLink"
                        :class="['shrink-0 min-w-10 h-10', { 'bg-highlight!': page + 1 === pageLink }]"
                        :text="page + 1 !== pageLink"
                        rounded
                        @click="() => changePageCallback(pageLink - 1)"
                    >{{ pageLink }}
                    </SecondaryButton>
                </div>
                <SecondaryButton :disabled="page === pageCount! - 1" rounded text @click="nextPageCallback">
                    <template #icon>
                        <AngleRightIcon/>
                    </template>
                </SecondaryButton>
                <SecondaryButton :disabled="page === pageCount! - 1" rounded text @click="lastPageCallback">
                    <template #icon>
                        <AngleDoubleRightIcon/>
                    </template>
                </SecondaryButton>
            </div>
        </template>
        <template v-for="(_, slotName) in $slots" #[slotName]="slotProps">
            <slot :name="slotName" v-bind="slotProps ?? {}"/>
        </template>
    </Paginator>
</template>

<script lang="ts" setup>
import AngleDoubleLeftIcon from '@primevue/icons/angledoubleleft';
import AngleDoubleRightIcon from '@primevue/icons/angledoubleright';
import AngleLeftIcon from '@primevue/icons/angleleft';
import AngleRightIcon from '@primevue/icons/angleright';
import Paginator, {type PaginatorPassThroughOptions, type PaginatorProps} from 'primevue/paginator';
import {ref} from 'vue'
import SecondaryButton from './SecondaryButton.vue';
import {ptViewMerge} from './utils';

defineProps</* @vue-ignore */ PaginatorProps>();

const theme = ref<PaginatorPassThroughOptions>({
    root: `flex items-center justify-center flex-wrap py-2 px-4 rounded-md gap-1
        bg-surface-0 dark:bg-surface-900 text-surface-700 dark:text-surface-0`
});
</script>
