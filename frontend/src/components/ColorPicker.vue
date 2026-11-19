<script setup>
import { CheckIcon } from '@heroicons/vue/24/outline'

import { cardColorOptions } from '../utils/cardColors'

defineProps({
  modelValue: { type: String, default: 'purple' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <!-- Seletor de cor em grade grande (T-045/usabilidade): passar o mouse
       destaca a amostra; o clique escolhe a cor do cartão. -->
  <div role="radiogroup" aria-label="Cor do cartão" class="grid grid-cols-5 gap-3 sm:grid-cols-6">
    <button
      v-for="option in cardColorOptions"
      :key="option.value"
      type="button"
      role="radio"
      :aria-checked="modelValue === option.value"
      :aria-label="option.label"
      :title="option.label"
      class="flex h-14 items-center justify-center rounded-xl bg-gradient-to-br shadow-card transition-transform hover:scale-110 hover:shadow-panel focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
      :class="[
        option.gradient,
        modelValue === option.value ? 'scale-110 ring-4 ring-primary ring-offset-2' : '',
      ]"
      @click="emit('update:modelValue', option.value)"
    >
      <CheckIcon
        v-if="modelValue === option.value"
        class="h-6 w-6 text-white drop-shadow"
        aria-hidden="true"
      />
    </button>
  </div>
</template>
