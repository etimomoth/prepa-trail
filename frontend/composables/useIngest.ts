import type { JobOut } from '~/types/api'

export function useIngest() {
  const { request, base } = useApi()
  const job = ref<JobOut | null>(null)
  const error = ref<string | null>(null)

  async function start(folder: string, recursive = true) {
    error.value = null
    const res = await request<{ job_id: number; scheduled: number }>('/ingest', {
      method: 'POST',
      body: JSON.stringify({ folder, recursive }),
    })
    follow(res.job_id)
    return res
  }

  function follow(jobId: number) {
    const src = new EventSource(`${base}/jobs/${jobId}/events`)
    src.addEventListener('progress', (e) => {
      job.value = JSON.parse((e as MessageEvent).data) as JobOut
      if (job.value.status === 'done' || job.value.status === 'error') src.close()
    })
    src.addEventListener('error', () => {
      error.value = 'stream error'
      src.close()
    })
  }

  return { job, error, start, follow }
}
