<script setup>
defineProps({
  // Itens: [{ value, label, count }]
  items: { type: Array, default: () => [] },
  modelValue: { type: [String, Number], default: '' },
  variant: {
    type: String,
    default: 'tabs',
    validator: (value) => ['tabs', 'pills'].includes(value),
  },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div
    v-if="variant === 'tabs'"
    class="flex flex-wrap gap-1 border-b border-neutral-200"
    role="tablist"
  >
    <button
      v-for="item in items"
      :key="item.value"
      type="button"
      role="tab"
      class="-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors"
      :class="
        item.value === modelValue
          ? 'border-primary text-primary'
          : 'border-transparent text-neutral-500 hover:text-neutral-700'
      "
      :aria-selected="item.value === modelValue"
      @click="$emit('update:modelValue', item.value)"
    >
      {{ item.label }}
    </button>
  </div>

  <div v-else class="flex flex-wrap gap-2" role="tablist">
    <button
      v-for="item in items"
      :key="item.value"
      type="button"
      role="tab"
      class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
      :class="
        item.value === modelValue
          ? 'bg-primary text-white'
          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
      "
      :aria-selected="item.value === modelValue"
      @click="$emit('update:modelValue', item.value)"
    >
      {{ item.label }}
    </button>
  </div>
</template>
