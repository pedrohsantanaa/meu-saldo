<script setup>
defineProps({
  caption: { type: String, default: '' },
  empty: { type: Boolean, default: false },
})
</script>

<template>
  <div class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card">
    <table class="w-full min-w-[36rem] text-left text-sm">
      <caption v-if="caption" class="sr-only">
        {{
          caption
        }}
      </caption>
      <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
        <slot name="head" />
      </thead>
      <tbody class="divide-y divide-neutral-100">
        <slot />
      </tbody>
    </table>

    <p v-if="empty" class="p-6 text-center text-sm text-neutral-500">Nenhum registro encontrado.</p>
  </div>
</template>
