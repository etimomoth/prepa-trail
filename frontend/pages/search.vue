<script setup lang="ts">
const { hits, loading, error, query } = useSearch()

async function onSubmit(q: string) {
  await query(q)
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Search</h1>
    <SearchBar @submit="onSubmit" />
    <p v-if="loading" class="text-neutral-500 text-sm">Searching…</p>
    <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

    <div v-if="hits.length" class="grid gap-2 grid-cols-3 sm:grid-cols-4 md:grid-cols-6">
      <figure
        v-for="h in hits"
        :key="h.photo.id"
        class="aspect-square overflow-hidden rounded bg-neutral-900 relative"
      >
        <img
          v-if="h.photo.thumb_path"
          :src="useApi().thumbUrl(h.photo.thumb_path)"
          loading="lazy"
          class="w-full h-full object-cover"
        />
        <span
          class="absolute bottom-1 left-1 text-[10px] bg-black/60 px-1.5 py-0.5 rounded"
        >
          {{ h.score.toFixed(2) }}
        </span>
      </figure>
    </div>
  </div>
</template>
