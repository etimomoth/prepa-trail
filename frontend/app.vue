<script setup lang="ts">
const route = useRoute()
const links = [
  { to: '/', label: 'Ingest' },
  { to: '/clusters', label: 'Clusters' },
  { to: '/timeline', label: 'Timeline' },
  { to: '/search', label: 'Search' },
]
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-neutral-800 sticky top-0 z-20 bg-neutral-950/90 backdrop-blur">
      <div class="max-w-6xl mx-auto flex items-center justify-between px-6 py-3">
        <NuxtLink to="/" class="font-semibold tracking-tight">photos-ai</NuxtLink>
        <nav class="flex gap-4 text-sm">
          <NuxtLink
            v-for="l in links"
            :key="l.to"
            :to="l.to"
            :class="[
              'px-2 py-1 rounded hover:text-white transition-colors',
              route.path === l.to ? 'text-white bg-neutral-800' : 'text-neutral-400',
            ]"
          >
            {{ l.label }}
          </NuxtLink>
        </nav>
      </div>
    </header>
    <main class="max-w-6xl mx-auto px-6 py-8">
      <NuxtPage />
    </main>
  </div>
</template>
