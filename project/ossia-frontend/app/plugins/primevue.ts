import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';

export default defineNuxtPlugin((app) => {
    app.vueApp.use(PrimeVue, {
        unstyled: true,
        options: {
            darkModeSelector: '.dark-mode'
        }
    });
    app.vueApp.use(ToastService)
})