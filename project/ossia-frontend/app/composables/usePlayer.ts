export default function () {
    const audio = new Audio()
    const currentTrack = ref<string | null>(null)
    const isPlaying = ref<boolean>(false)

    /*function load() {
        audio.src =
        audio.load()
    }*/

    async function play() {
        const promise = audio.play()
        if (promise) {
            await promise
        }
    }

    return {
        play,
        isPlaying, currentTrack
    }
}