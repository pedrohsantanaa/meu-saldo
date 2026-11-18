<script setup>
import { computed } from 'vue'

import { addMonths, formatMonthYear, isSameMonth } from '../utils/period'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  modelValue: { type: Date, required: true },
})

const emit = defineEmits(['update:modelValue'])

const label = computed(() => formatMonthYear(props.modelValue))
const showToday = computed(() => !isSameMonth(props.modelValue, new Date()))

function go(delta) {
  emit('update:modelValue', addMonths(props.modelValue, delta))
}

function goToday() {
  const today = new Date()
  emit('update:modelValue', new Date(today.getFullYear(), today.getMonth(), 1))
}
</script>

<template>
  <div class="flex items-center gap-2">
    <div
      class="flex items-center gap-1 rounded-card border border-neutral-200 bg-white px-1 py-1 shadow-card"
    >
      <button
        type="button"
        class="rounded-md px-2 py-1 text-neutral-500 hover:bg-neutral-100"
        aria-label="Mês anterior"
        @click="go(-1)"
      >
        &lsaquo;
      </button>

      <p class="min-w-[9rem] text-center text-sm font-semibold text-neutral-900" aria-live="polite">
        {{ label }}
      </p>

      <button
        type="button"
        class="rounded-md px-2 py-1 text-neutral-500 hover:bg-neutral-100"
        aria-label="Próximo mês"
        @click="go(1)"
      >
        &rsaquo;
      </button>
    </div>

    <BaseButton v-if="showToday" variant="secondary" size="sm" @click="goToday">Hoje</BaseButton>
  </div>
</template>
