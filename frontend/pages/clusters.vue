<script setup lang="ts">
import type { ClusterOut, PhotoOut } from '~/types/api'

const { clusters, fetchAll, photosOf, recluster } = useClusters()
const opened = ref<number | null>(null)
const openedPhotos = ref<PhotoOut[]>([])

await fetchAll()

async function toggle(c: ClusterOut) {
  if (opened.value === c.id) {
    opened.value = null
    openedPhotos.value = []
    return
  }
  opened.value = c.id
  openedPhotos.value = await photosOf(c.id)
}

async function onRecluster() {
  await recluster()
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-baseline justify-between">
      <h1 class="text-2xl font-bold">Clusters</h1>
      <button
        class="text-sm px-3 py-1 rounded border border-neutral-700 hover:bg-neutral-900"
        @click="onRecluster"
      >
        Recluster
      </button>
    </div>

    <p v-if="!clusters.length" class="text-neutral-500">
      No clusters yet. Ingest some photos first.
    </p>

    <ul class="space-y-3">
      <li
        v-for="c in clusters"
        :key="c.id"
        class="rounded-lg border border-neutral-800 bg-neutral-900/40"
      >
        <button
          class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-900"
          @click="toggle(c)"
        >
          <span class="font-medium">{{ c.label }}</span>
          <span class="text-xs text-neutral-500">{{ c.photo_count }} photos</span>
        </button>
        <div v-if="opened === c.id" class="p-4 border-t border-neutral-800">
          <PhotoGrid :photos="openedPhotos" />
        </div>
      </li>
    </ul>
  </div>
</template>
