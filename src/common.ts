import { writable } from "svelte/store"

export const apiLocation = "http://localhost:8000"

export const knownTags = writable<string[]>([])
