<script setup>
defineProps({
  variant: {
    type: String,
    default: 'neutral',
    validator: (value) =>
      ['neutral', 'income', 'expense', 'fixed', 'variable', 'investment'].includes(value),
  },
})

const variants = {
  neutral: 'bg-neutral-100 text-neutral-600',
  income: 'bg-positive-light text-positive',
  expense: 'bg-negative-light text-negative',
  fixed: 'bg-negative-light text-negative',
  variable: 'bg-attention-light text-attention',
  investment: 'bg-investment-light text-investment',
}
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
    :class="variants[variant]"
  >
    <slot />
  </span>
</template>
