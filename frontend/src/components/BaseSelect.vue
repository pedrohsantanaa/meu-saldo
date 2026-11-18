<script setup>
import { useId } from 'vue'

defineOptions({ inheritAttrs: false })

defineProps({
  label: { type: String, default: '' },
  modelValue: { type: [String, Number], default: '' },
  options: {
    type: Array,
    default: () => [],
  },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: 'Selecione...' },
})

defineEmits(['update:modelValue'])

const id = useId()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" :for="id" class="text-sm font-medium text-neutral-700">
      {{ label }}
    </label>

    <select
      :id="id"
      v-bind="$attrs"
      :value="modelValue"
      :disabled="disabled"
      :aria-invalid="Boolean(error)"
      :aria-describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined"
      class="w-full rounded-md border bg-white px-3 py-2 text-sm text-neutral-900 disabled:cursor-not-allowed disabled:bg-neutral-100"
      :class="error ? 'border-negative' : 'border-neutral-300'"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>

    <p v-if="hint && !error" :id="`${id}-hint`" class="text-xs text-neutral-500">
      {{ hint }}
    </p>

    <p v-if="error" :id="`${id}-error`" role="alert" class="text-xs text-negative">
      {{ error }}
    </p>
  </div>
</template>
