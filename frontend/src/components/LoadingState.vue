<script setup>
defineProps({
  label: { type: String, default: 'Carregando...' },
})
</script>

<template>
  <div class="flex items-center justify-center gap-3 p-8 text-sm text-neutral-500" aria-busy="true">
    <span class="h-5 w-5 animate-spin rounded-full border-2 border-neutral-300 border-t-primary" />
    {{ label }}
  </div>
</template>
