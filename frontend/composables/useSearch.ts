import type { SearchHit } from '~/types/api'

export function useSearch() {
  const { request } = useApi()
  const hits = ref<SearchHit[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function query(q: string, k = 24) {
    loading.value = true
    error.value = null
    try {
      hits.value = await request<SearchHit[]>('/search', {
        method: 'POST',
        body: JSON.stringify({ query: q, k }),
      })
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  return { hits, loading, error, query }
}
