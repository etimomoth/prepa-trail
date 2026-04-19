<script setup lang="ts">
const { job, error, uploading, uploadFiles } = useIngest()
const pendingCount = ref(0)

async function onFiles(files: File[]) {
  pendingCount.value = files.length
  try {
    await uploadFiles(files)
  } catch {
    /* surfaced via error */
  }
}
</script>

<template>
  <div class="space-y-8">
    <section>
      <h1 class="text-3xl font-bold mb-3">Drop. Organize. Find.</h1>
      <p class="text-neutral-400 max-w-2xl">
        Drop a batch of photos below. They're hashed, embedded with CLIP locally,
        and auto-grouped into events by visual similarity + time + GPS.
      </p>
    </section>

    <Dropzone @files="onFiles" />

    <div v-if="uploading" class="text-sm text-neutral-400">
      Uploading {{ pendingCount }} file{{ pendingCount === 1 ? '' : 's' }}…
    </div>

    <ProgressBar
      v-if="job"
      :progress="job.progress"
      :total="job.total"
      :status="job.status"
      :message="job.message"
    />

    <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

    <div v-if="job?.status === 'done'" class="flex gap-4 pt-2">
      <NuxtLink
        to="/clusters"
        class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-sm font-medium"
      >
        Browse clusters →
      </NuxtLink>
      <NuxtLink
        to="/search"
        class="px-4 py-2 rounded border border-neutral-700 hover:bg-neutral-900 text-sm"
      >
        Search
      </NuxtLink>
    </div>
  </div>
</template>
