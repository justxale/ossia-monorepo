import {twMerge} from 'tailwind-merge';
import {mergeProps} from 'vue';

type Props = {
    "class"?: string
    [p: string]: string | undefined | never
}

export const ptViewMerge = (globalPTProps: Props = {}, selfPTProps: Props = {}, datasets: Props = {}) => {
    const {class: globalClass, ...globalRest} = globalPTProps;
    const {class: selfClass, ...selfRest} = selfPTProps;

    return mergeProps({class: twMerge(globalClass, selfClass)}, globalRest, selfRest, datasets);
};
