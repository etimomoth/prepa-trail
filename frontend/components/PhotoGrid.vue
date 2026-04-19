<script setup lang="ts">
import type { PhotoOut } from '~/types/api'

defineProps<{ photos: PhotoOut[] }>()

const { thumbUrl } = useApi()
</script>

<template>
  <div class="grid gap-2 grid-cols-3 sm:grid-cols-4 md:grid-cols-6">
    <figure
      v-for="p in photos"
      :key="p.id"
      class="aspect-square overflow-hidden rounded bg-neutral-900 group relative"
    >
      <img
        v-if="p.thumb_path"
        :src="thumbUrl(p.thumb_path)"
        :alt="p.caption ?? p.scene ?? 'photo'"
        loading="lazy"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      <figcaption
        v-if="p.scene"
        class="absolute bottom-1 left-1 text-[10px] uppercase tracking-wider bg-black/60 px-1.5 py-0.5 rounded"
      >
        {{ p.scene }}
      </figcaption>
    </figure>
  </div>
</template>
