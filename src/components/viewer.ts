import { Writable, writable } from "svelte/store"

export class SyncedMedia {
    private _currentTime: number
    sources: HTMLMediaElement[]
    buffering: Writable<boolean[]>

    constructor(sources: HTMLMediaElement[]) {
        this._currentTime = 0
        this.sources = sources

        this.buffering = writable<boolean[]>([])
        for (let i = 0; i < sources.length; i++) {
            const s = sources[i]
            this.buffering.update(states => [...states, false])
            s.addEventListener("waiting", () => {
                this.buffering.update(states => {
                    states[i] = true
                    return states
                })
            })
            s.addEventListener("playing", () => {
                this.buffering.update(states => {
                    states[i] = false
                    return states
                })
            })
        }
        this.buffering.subscribe((states) => {
            let buffering = false
            for (let i = 0; i < states.length; i++) {
                if (states[i]) {
                    buffering = true
                }
            }

            if (buffering) {
                for (let i = 0; i < this.sources.length; i++) {
                    if (!states[i]) {
                        this.sources[i].pause()
                        continue
                    }
                    this.sources[i].play()
                }
                return
            }

            this.play()
        })

        this.sources[0].addEventListener("timeupdate", () => {
            this._currentTime = this.sources[0].currentTime
        })
    }

    get duration(): number {
        return this.sources[0].duration
    }

    get currentTime(): number {
        return this._currentTime
    }

    set currentTime(time: number) {
        this._currentTime = time
        for (const s of this.sources) {
            s.currentTime = time
        }
    }

    play(exclude?: number[]) {
        for (let i = 0; i < this.sources.length; i++) {
            if (exclude?.includes(i)) {
                continue
            }
            this.sources[i].play()
        }
    }

    pause(exclude?: number[]) {
        const syncTime = this.sources[0].currentTime
        for (let i = 0; i < this.sources.length; i++) {
            if (exclude?.includes(i)) {
                continue
            }
            this.sources[i].pause()
            this.sources[i].currentTime = syncTime
        }
    }

    fastSeek(time: number) {
        for (const s of this.sources) {
            s.fastSeek(time)
        }
    }
}
