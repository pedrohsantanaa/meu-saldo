<script setup>
import { onBeforeUnmount, onMounted } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
})

const emit = defineEmits(['update:open'])

function onKeydown(event) {
  if (event.key === 'Escape' && props.open) {
    emit('update:open', false)
  }
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      :aria-label="title"
    >
      <div
        class="absolute inset-0 bg-black/40"
        aria-hidden="true"
        @click="emit('update:open', false)"
      />

      <div class="relative w-full max-w-md rounded-card bg-white p-6 shadow-panel">
        <div class="mb-4 flex items-start justify-between gap-4">
          <h2 class="text-lg">{{ title }}</h2>
          <button
            type="button"
            class="rounded-md p-1 text-neutral-500 hover:bg-neutral-100"
            aria-label="Fechar"
            @click="emit('update:open', false)"
          >
            <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path
                d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"
              />
            </svg>
          </button>
        </div>

        <slot />

        <div v-if="$slots.footer" class="mt-6 flex justify-end gap-2">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
