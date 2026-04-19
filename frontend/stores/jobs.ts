import { defineStore } from 'pinia'
import type { JobOut } from '~/types/api'

export const useJobsStore = defineStore('jobs', () => {
  const active = ref<JobOut | null>(null)

  function set(job: JobOut | null) {
    active.value = job
  }

  const percent = computed(() => {
    if (!active.value || active.value.total === 0) return 0
    return Math.round((active.value.progress / active.value.total) * 100)
  })

  return { active, percent, set }
})
