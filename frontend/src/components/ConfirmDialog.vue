<script setup>
import BaseButton from './BaseButton.vue'
import BaseModal from './BaseModal.vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmar operação' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:open', 'confirm'])
</script>

<template>
  <BaseModal :open="open" :title="title" @update:open="emit('update:open', $event)">
    <p class="text-sm text-neutral-600">{{ message }}</p>

    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:open', false)">
        {{ cancelLabel }}
      </BaseButton>
      <BaseButton variant="danger" :loading="loading" @click="emit('confirm')">
        {{ confirmLabel }}
      </BaseButton>
    </template>
  </BaseModal>
</template>
