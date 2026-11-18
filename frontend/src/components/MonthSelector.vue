<script setup>
import { computed } from 'vue'

import { addMonths, addYears, formatMonthYear, formatYear, isSameMonth } from '../utils/period'
import BaseButton from './BaseButton.vue'
import BaseSelect from './BaseSelect.vue'

const props = defineProps({
  modelValue: { type: Date, required: true },
  mode: {
    type: String,
    default: 'mensal',
    validator: (value) => ['mensal', 'anual'].includes(value),
  },
})

const emit = defineEmits(['update:modelValue', 'update:mode'])

const isMensal = computed(() => props.mode === 'mensal')

const label = computed(() =>
  isMensal.value ? formatMonthYear(props.modelValue) : formatYear(props.modelValue)
)

const yearOptions = computed(() => {
  const base = props.modelValue.getFullYear()
  return Array.from({ length: 21 }, (_, index) => {
    const year = base - 10 + index
    return { value: String(year), label: String(year) }
  })
})

const showToday = computed(() => !isSameMonth(props.modelValue, new Date()))

function go(delta) {
  const next = isMensal.value
    ? addMonths(props.modelValue, delta)
    : addYears(props.modelValue, delta)
  emit('update:modelValue', next)
}

function goToday() {
  const today = new Date()
  emit('update:modelValue', new Date(today.getFullYear(), today.getMonth(), 1))
}

function onYearChange(year) {
  const month = isMensal.value ? props.modelValue.getMonth() : 0
  emit('update:modelValue', new Date(Number(year), month, 1))
}

function setMode(mode) {
  emit('update:mode', mode)
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <div class="flex items-center gap-1">
      <BaseButton
        variant="secondary"
        size="sm"
        :aria-label="isMensal ? 'Mês anterior' : 'Ano anterior'"
        @click="go(-1)"
      >
        &lsaquo;
      </BaseButton>

      <p class="min-w-[10rem] text-center text-lg font-semibold" aria-live="polite">
        {{ label }}
      </p>

      <BaseButton
        variant="secondary"
        size="sm"
        :aria-label="isMensal ? 'Próximo mês' : 'Próximo ano'"
        @click="go(1)"
      >
        &rsaquo;
      </BaseButton>
    </div>

    <BaseButton v-if="showToday" variant="ghost" size="sm" @click="goToday">Hoje</BaseButton>

    <BaseSelect
      :model-value="String(modelValue.getFullYear())"
      :options="yearOptions"
      class="w-28"
      aria-label="Selecionar ano"
      @update:model-value="onYearChange"
    />

    <div class="ml-auto flex items-center rounded-md border border-neutral-300 bg-white p-0.5">
      <button
        type="button"
        class="rounded px-3 py-1.5 text-sm font-medium transition-colors"
        :class="isMensal ? 'bg-primary text-white' : 'text-neutral-600 hover:bg-neutral-100'"
        :aria-pressed="isMensal"
        @click="setMode('mensal')"
      >
        Mensal
      </button>
      <button
        type="button"
        class="rounded px-3 py-1.5 text-sm font-medium transition-colors"
        :class="!isMensal ? 'bg-primary text-white' : 'text-neutral-600 hover:bg-neutral-100'"
        :aria-pressed="!isMensal"
        @click="setMode('anual')"
      >
        Anual
      </button>
    </div>
  </div>
</template>
