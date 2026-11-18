<script setup>
import { useId } from 'vue'

defineOptions({ inheritAttrs: false })

defineProps({
  label: { type: String, default: '' },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

defineEmits(['update:modelValue'])

const id = useId()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" :for="id" class="text-sm font-medium text-neutral-700">
      {{ label }}
    </label>

    <input
      :id="id"
      v-bind="$attrs"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :aria-invalid="Boolean(error)"
      :aria-describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined"
      class="w-full rounded-md border bg-white px-3 py-2 text-sm text-neutral-900 placeholder:text-neutral-400 disabled:cursor-not-allowed disabled:bg-neutral-100"
      :class="error ? 'border-negative' : 'border-neutral-300'"
      @input="$emit('update:modelValue', $event.target.value)"
    />

    <p v-if="hint && !error" :id="`${id}-hint`" class="text-xs text-neutral-500">
      {{ hint }}
    </p>

    <p v-if="error" :id="`${id}-error`" role="alert" class="text-xs text-negative">
      {{ error }}
    </p>
  </div>
</template>
