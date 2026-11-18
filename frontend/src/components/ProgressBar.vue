<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  showLabel: { type: Boolean, default: true },
})

const percentage = computed(() => {
  if (!props.max) return 0
  return Math.min(100, Math.round((props.value / props.max) * 100))
})

const colorClass = computed(() => {
  if (percentage.value >= 100) return 'bg-negative'
  if (percentage.value >= 80) return 'bg-attention'
  return 'bg-positive'
})
</script>

<template>
  <div class="flex items-center gap-3">
    <div class="h-2 flex-1 overflow-hidden rounded-full bg-neutral-200">
      <div class="h-full rounded-full" :class="colorClass" :style="{ width: `${percentage}%` }" />
    </div>
    <span v-if="showLabel" class="w-24 shrink-0 text-right text-xs text-neutral-500">
      {{ percentage }}% utilizado
    </span>
  </div>
</template>
