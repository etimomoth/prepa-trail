<script setup lang="ts">
const q = ref('')
const emit = defineEmits<{ submit: [query: string] }>()

function submit() {
  if (!q.value.trim()) return
  emit('submit', q.value.trim())
}
</script>

<template>
  <form class="flex gap-2" @submit.prevent="submit">
    <input
      v-model="q"
      type="search"
      placeholder="sunset over the ocean…"
      class="flex-1 bg-neutral-950 border border-neutral-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-neutral-600"
    />
    <button
      type="submit"
      class="px-4 py-2 rounded bg-white text-neutral-950 text-sm font-medium hover:bg-neutral-200"
    >
      Search
    </button>
  </form>
</template>
