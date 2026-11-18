<script setup>
defineProps({
  title: { type: String, default: 'Nenhum registro encontrado' },
  description: { type: String, default: '' },
})
</script>

<template>
  <div
    class="flex flex-col items-center gap-2 rounded-card border border-dashed border-neutral-300 bg-white p-8 text-center"
  >
    <svg
      class="mb-1 h-10 w-10 text-neutral-300"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      aria-hidden="true"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.444-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H6.911a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661Z"
      />
    </svg>

    <p class="font-medium text-neutral-700">{{ title }}</p>
    <p v-if="description" class="max-w-sm text-sm text-neutral-500">{{ description }}</p>

    <div v-if="$slots.actions" class="mt-2">
      <slot name="actions" />
    </div>
  </div>
</template>
