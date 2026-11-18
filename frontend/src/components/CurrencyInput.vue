<script setup>
import { ref, useId, watch } from 'vue'

import { formatCurrency } from '../utils/formatCurrency'
import { parseCurrency } from '../utils/parseCurrency'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  label: { type: String, default: '' },
  placeholder: { type: String, default: 'R$ 0,00' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const id = useId()
const focused = ref(false)
const display = ref(formatCurrency(props.modelValue))

watch(
  () => props.modelValue,
  (value) => {
    if (!focused.value) display.value = formatCurrency(value)
  }
)

function onInput(event) {
  display.value = event.target.value
  emit('update:modelValue', parseCurrency(event.target.value))
}

function onFocus() {
  focused.value = true
}

function onBlur(event) {
  focused.value = false
  const value = parseCurrency(event.target.value)
  emit('update:modelValue', value)
  display.value = formatCurrency(value)
}
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" :for="id" class="text-sm font-medium text-neutral-700">
      {{ label }}
    </label>

    <input
      :id="id"
      v-bind="$attrs"
      type="text"
      inputmode="decimal"
      :value="display"
      :placeholder="placeholder"
      :disabled="disabled"
      :aria-invalid="Boolean(error)"
      :aria-describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined"
      class="w-full rounded-md border bg-white px-3 py-2 text-right text-sm tabular-nums text-neutral-900 placeholder:text-neutral-400 disabled:cursor-not-allowed disabled:bg-neutral-100"
      :class="error ? 'border-negative' : 'border-neutral-300'"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    />

    <p v-if="hint && !error" :id="`${id}-hint`" class="text-xs text-neutral-500">
      {{ hint }}
    </p>

    <p v-if="error" :id="`${id}-error`" role="alert" class="text-xs text-negative">
      {{ error }}
    </p>
  </div>
</template>
