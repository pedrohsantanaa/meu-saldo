<script setup>
defineProps({ title: { type: String, default: '' } })
</script>

<template>
  <section>
    <h1 class="mb-1 text-2xl font-semibold">{{ title || $route.meta.title }}</h1>
    <div class="mt-6 rounded-lg border border-dashed border-neutral-300 bg-white p-8 text-center">
      <p class="text-neutral-600">Funcionalidade prevista para as próximas fases.</p>
    </div>
  </section>
</template>
