// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
    experimental: {
        writeEarlyHints: true,
    },

    app: {
        rootAttrs: {
            id: 'root'
        },
        head: {
            htmlAttrs: {
                lang: "ru",
            }
        }
    },
    compatibilityDate: '2025-07-15',
    devtools: {enabled: true},
    modules: [
      '@nuxt/image',
      '@nuxt/eslint',
      '@pinia/nuxt',
      '@vueuse/nuxt',
      '@nuxtjs/seo',
      '@nuxtjs/color-mode',
    ],
    vite: {
        plugins: [tailwindcss()],
        server: {
            hmr: true,
            allowedHosts: ['lh.justxale.com'],
        },
    },
    css: ['~/assets/css/tailwind.css', '~/assets/css/index.css'],
    typescript: {
        typeCheck: true
    },
    colorMode: {
        preference: "system",
        fallback: 'dark',
        storageKey: "color-mode"
    }

})