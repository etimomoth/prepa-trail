import type { JobOut } from '~/types/api'

export function useIngest() {
  const { base } = useApi()
  const job = ref<JobOut | null>(null)
  const error = ref<string | null>(null)
  const uploading = ref(false)

  async function uploadFiles(files: File[]) {
    error.value = null
    uploading.value = true
    try {
      const form = new FormData()
      for (const f of files) form.append('files', f, f.name)
      const res = await fetch(`${base}/ingest/upload`, { method: 'POST', body: form })
      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`)
      const data = (await res.json()) as { job_id: number; scheduled: number }
      follow(data.job_id)
      return data
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      uploading.value = false
    }
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

  return { job, error, uploading, uploadFiles, follow }
}
