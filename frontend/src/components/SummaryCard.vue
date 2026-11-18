<script setup>
import { computed } from 'vue'

import { formatCurrency } from '../utils/formatCurrency'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  tone: {
    type: String,
    default: 'neutral',
    validator: (value) => ['neutral', 'positive', 'negative', 'investment', 'variable'].includes(value),
  },
  icon: { type: [Object, Function], default: null },
  hint: { type: String, default: '' },
})

const displayValue = computed(() =>
  typeof props.value === 'number' ? formatCurrency(props.value) : props.value
)

const tones = {
  neutral: { badge: 'bg-positive-light text-positive', value: 'text-neutral-900' },
  positive: { badge: 'bg-positive-light text-positive', value: 'text-positive' },
  negative: { badge: 'bg-negative-light text-negative', value: 'text-negative' },
  investment: { badge: 'bg-investment-light text-investment', value: 'text-neutral-900' },
  variable: { badge: 'bg-variable-light text-variable', value: 'text-neutral-900' },
}
</script>

<template>
  <div class="flex items-center gap-3 rounded-card border border-neutral-200 bg-white p-4 shadow-card">
    <span
      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
      :class="tones[tone].badge"
    >
      <component :is="icon" v-if="icon" class="h-5 w-5" aria-hidden="true" />
      <span v-else aria-hidden="true">$</span>
    </span>

    <div class="min-w-0">
      <p class="text-sm text-neutral-500">{{ label }}</p>
      <p class="truncate text-xl font-semibold" :class="tones[tone].value">
        {{ displayValue }}
      </p>
      <p v-if="hint" class="text-xs text-neutral-400">{{ hint }}</p>
    </div>
  </div>
</template>
