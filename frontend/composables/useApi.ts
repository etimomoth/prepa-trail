export function useApi() {
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${base}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
      ...init,
    })
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`)
    return res.json() as Promise<T>
  }

  function thumbUrl(thumbPath: string | null | undefined): string {
    if (!thumbPath) return ''
    const name = thumbPath.split('/').slice(-2).join('/')
    return `${base}/thumbs/${name}`
  }

  return { base, request, thumbUrl }
}
