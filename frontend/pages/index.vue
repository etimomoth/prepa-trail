<script setup lang="ts">
const { job, error, start } = useIngest()
const { recluster } = useClusters()

async function onSubmit(folder: string) {
  await start(folder)
}

watch(
  () => job.value?.status,
  async (s) => {
    if (s === 'done') await recluster()
  }
)
</script>

<template>
  <div class="space-y-6">
    <section>
      <h1 class="text-2xl font-bold mb-4">Drop. Organize. Find.</h1>
      <p class="text-neutral-400 mb-6 max-w-2xl">
        Point photos-ai at a folder of photos. CLIP embeddings are computed locally, then photos are
        auto-clustered into events based on visual similarity, time, and GPS.
      </p>
      <Dropzone @submit="onSubmit" />
    </section>

    <ProgressBar
      v-if="job"
      :progress="job.progress"
      :total="job.total"
      :status="job.status"
      :message="job.message"
    />

    <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

    <div v-if="job?.status === 'done'" class="pt-4">
      <NuxtLink to="/clusters" class="underline decoration-neutral-600">
        Browse clusters →
      </NuxtLink>
    </div>
  </div>
</template>
