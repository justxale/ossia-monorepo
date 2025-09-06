export default defineNuxtPlugin(async (app) => {
    const config = await app.runWithContext(useAppConfig)

    const api = $fetch.create({
        baseURL: config.baseURL + config.apiEndpoint,
        async onRequest({options}) {
            const token = await app.runWithContext(() => useCookie('access_token'))
            if (token.value) {
                // note that this relies on ofetch >= 1.4.0 - you may need to refresh your lockfile
                options.headers.set('Authorization', `Bearer ${token.value}`)
            }
        }
    })

    return {
        provide: {
            api
        }
    }
})