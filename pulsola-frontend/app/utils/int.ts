export type ParsedDuration = {
    seconds: number
    minutes: number
    hours: number
}

export function parseDuration(seconds: number): ParsedDuration {
    return {
        seconds: (seconds % 60) | 0,
        minutes: (seconds / 60) % 60 | 0,
        hours: (seconds / (60 * 60)) | 0
    }
}