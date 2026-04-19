<script setup lang="ts">
const emit = defineEmits<{ files: [files: File[]] }>()
const dragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const IMG_RE = /\.(jpe?g|png|webp|heic|tiff?|bmp)$/i

function filter(list: FileList | File[]): File[] {
  return Array.from(list).filter((f) => IMG_RE.test(f.name))
}

function onDrop(e: DragEvent) {
  dragging.value = false
  if (!e.dataTransfer?.files.length) return
  const images = filter(e.dataTransfer.files)
  if (images.length) emit('files', images)
}

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const images = filter(input.files)
  if (images.length) emit('files', images)
  input.value = ''
}
</script>

<template>
  <div
    :class="[
      'rounded-2xl border-2 border-dashed p-10 text-center transition-colors',
      dragging
        ? 'border-emerald-500 bg-emerald-500/5'
        : 'border-neutral-700 bg-neutral-900/40 hover:border-neutral-500',
    ]"
    @dragenter.prevent="dragging = true"
    @dragover.prevent="dragging = true"
    @dragleave.prevent="dragging = false"
    @drop.prevent="onDrop"
  >
    <p class="text-lg font-medium mb-2">Drop photos here</p>
    <p class="text-sm text-neutral-400 mb-4">
      JPG, PNG, WebP, HEIC — processed locally.
    </p>
    <button
      type="button"
      class="px-4 py-2 rounded bg-white text-neutral-950 text-sm font-medium hover:bg-neutral-200"
      @click="fileInput?.click()"
    >
      Or pick files…
    </button>
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      multiple
      class="hidden"
      @change="onPick"
    />
  </div>
</template>
