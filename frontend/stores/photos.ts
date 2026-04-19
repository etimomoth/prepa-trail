import { defineStore } from 'pinia'
import type { PhotoOut } from '~/types/api'

export const usePhotosStore = defineStore('photos', () => {
  const byId = ref<Record<number, PhotoOut>>({})

  function upsert(list: PhotoOut[]) {
    for (const p of list) byId.value[p.id] = p
  }

  const list = computed(() => Object.values(byId.value))

  return { byId, list, upsert }
})
