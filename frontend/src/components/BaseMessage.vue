<script setup>
defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'info', 'attention'].includes(value),
  },
  title: { type: String, default: '' },
})

const styles = {
  success: 'border-positive/30 bg-positive-light text-positive',
  error: 'border-negative/30 bg-negative-light text-negative',
  info: 'border-primary/30 bg-primary-light text-primary-dark',
  attention: 'border-attention/30 bg-attention-light text-attention',
}
</script>

<template>
  <div
    class="rounded-card border px-4 py-3 text-sm"
    :class="styles[type]"
    :role="type === 'error' ? 'alert' : 'status'"
  >
    <p v-if="title" class="font-medium">{{ title }}</p>
    <slot />
  </div>
</template>
