<script setup>
import { computed } from 'vue'

import { formatCurrency } from '../utils/formatCurrency'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  tone: {
    type: String,
    default: 'neutral',
    validator: (value) => ['neutral', 'positive', 'negative', 'attention'].includes(value),
  },
  hint: { type: String, default: '' },
})

const displayValue = computed(() =>
  typeof props.value === 'number' ? formatCurrency(props.value) : props.value
)

const toneClass = {
  neutral: 'text-neutral-900',
  positive: 'text-positive',
  negative: 'text-negative',
  attention: 'text-attention',
}
</script>

<template>
  <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
    <p class="text-sm text-neutral-500">{{ label }}</p>
    <p class="mt-1 text-xl font-semibold" :class="toneClass[tone]">
      {{ displayValue }}
    </p>
    <p v-if="hint" class="mt-1 text-xs text-neutral-400">{{ hint }}</p>
  </div>
</template>
