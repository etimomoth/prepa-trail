<script setup lang="ts">
const folder = ref('')
const emit = defineEmits<{ submit: [folder: string] }>()

function submit() {
  const v = folder.value.trim()
  if (!v) return
  emit('submit', v)
}
</script>

<template>
  <div class="rounded-2xl border border-dashed border-neutral-700 p-8 bg-neutral-900/40">
    <h2 class="text-xl font-semibold mb-2">Drop a folder</h2>
    <p class="text-sm text-neutral-400 mb-4">
      Browser APIs can't upload a folder path directly. Paste the absolute path on the server
      machine below — photos-ai is local-first.
    </p>
    <form class="flex gap-2" @submit.prevent="submit">
      <input
        v-model="folder"
        type="text"
        placeholder="/home/you/Pictures/2024"
        class="flex-1 bg-neutral-950 border border-neutral-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-neutral-600"
      />
      <button
        type="submit"
        class="px-4 py-2 rounded bg-white text-neutral-950 text-sm font-medium hover:bg-neutral-200"
      >
        Ingest
      </button>
    </form>
  </div>
</template>
