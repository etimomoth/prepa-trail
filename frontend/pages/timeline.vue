<script setup lang="ts">
const { clusters, fetchAll } = useClusters()
await fetchAll()

const byYear = computed(() => {
  const groups = new Map<string, typeof clusters.value>()
  for (const c of clusters.value) {
    const y = c.start_date ? c.start_date.slice(0, 4) : 'undated'
    const arr = groups.get(y) ?? []
    arr.push(c)
    groups.set(y, arr)
  }
  return [...groups.entries()].sort(([a], [b]) => (a < b ? 1 : -1))
})
</script>

<template>
  <div class="space-y-8">
    <h1 class="text-2xl font-bold">Timeline</h1>
    <section v-for="[year, group] in byYear" :key="year" class="space-y-3">
      <h2 class="text-neutral-400 text-sm uppercase tracking-widest">{{ year }}</h2>
      <ul class="grid gap-2 grid-cols-1 sm:grid-cols-2">
        <li
          v-for="c in group"
          :key="c.id"
          class="rounded border border-neutral-800 px-4 py-3 flex justify-between"
        >
          <NuxtLink :to="`/clusters#${c.id}`" class="font-medium">{{ c.label }}</NuxtLink>
          <span class="text-xs text-neutral-500">{{ c.photo_count }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>
