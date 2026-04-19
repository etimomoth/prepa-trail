import type { ClusterOut, PhotoOut } from '~/types/api'

export function useClusters() {
  const { request } = useApi()
  const clusters = ref<ClusterOut[]>([])

  async function fetchAll() {
    clusters.value = await request<ClusterOut[]>('/clusters')
  }

  async function photosOf(id: number): Promise<PhotoOut[]> {
    return request<PhotoOut[]>(`/clusters/${id}/photos`)
  }

  async function recluster() {
    await request('/clusters/recluster', { method: 'POST' })
  }

  return { clusters, fetchAll, photosOf, recluster }
}
