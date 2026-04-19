<script setup lang="ts">
const props = defineProps<{
  progress: number
  total: number
  status: string
  message?: string | null
}>()

const percent = computed(() => {
  if (!props.total) return 0
  return Math.min(100, Math.round((props.progress / props.total) * 100))
})
</script>

<template>
  <div class="rounded-xl bg-neutral-900 border border-neutral-800 p-4">
    <div class="flex justify-between text-sm mb-2">
      <span class="text-neutral-300">{{ status }}</span>
      <span class="text-neutral-500">{{ progress }}/{{ total }} ({{ percent }}%)</span>
    </div>
    <div class="h-2 rounded bg-neutral-800 overflow-hidden">
      <div
        class="h-full bg-emerald-500 transition-all duration-300"
        :style="{ width: `${percent}%` }"
      />
    </div>
    <p v-if="message" class="mt-2 text-xs text-neutral-500">{{ message }}</p>
  </div>
</template>
