<script setup>
import BaseButton from './BaseButton.vue'

defineProps({
  message: {
    type: String,
    default: 'Não foi possível carregar os dados.',
  },
})

const emit = defineEmits(['retry'])
</script>

<template>
  <!-- Estado de erro com nova tentativa (AC-080): nunca deixar o usuário
       preso em carregamento quando a API falha. -->
  <div
    role="alert"
    class="rounded-card border border-negative/20 bg-negative-light p-6 text-center"
  >
    <p class="text-sm text-negative">{{ message }}</p>
    <BaseButton variant="secondary" class="mt-4" @click="emit('retry')">
      Tentar novamente
    </BaseButton>
  </div>
</template>
