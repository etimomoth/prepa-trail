export interface PhotoOut {
  id: number
  sha256: string
  path: string
  thumb_path: string | null
  width: number | null
  height: number | null
  taken_at: string | null
  latitude: number | null
  longitude: number | null
  scene: string | null
  caption: string | null
  quality_score: number | null
  cluster_id: number | null
}

export interface ClusterOut {
  id: number
  label: string
  scene: string | null
  start_date: string | null
  end_date: string | null
  place: string | null
  photo_count: number
  cover_photo_id: number | null
}

export interface SearchHit {
  photo: PhotoOut
  score: number
}

export interface JobOut {
  id: number
  kind: string
  status: 'pending' | 'running' | 'done' | 'error'
  progress: number
  total: number
  message: string | null
  started_at: string
  ended_at: string | null
}
