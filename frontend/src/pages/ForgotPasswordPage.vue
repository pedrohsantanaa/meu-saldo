<script setup>
import { ref } from 'vue'

import BaseButton from '../components/BaseButton.vue'
import BaseInput from '../components/BaseInput.vue'
import { api } from '../services/api'

const email = ref('')
const error = ref('')
const sent = ref(false)
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await api.post('/auth/forgot-password', { email: email.value })
    sent.value = true
  } catch (err) {
    error.value = err.message || 'Não foi possível solicitar a redefinição. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-neutral-50 p-4">
    <div class="w-full max-w-sm rounded-card border border-neutral-200 bg-white p-6 shadow-panel">
      <h1 class="mb-1 text-center text-lg">Recuperar senha</h1>
      <p class="mb-6 text-center text-sm text-neutral-500">
        Informe seu e-mail para receber as instruções de redefinição.
      </p>

      <div
        v-if="sent"
        class="rounded-md bg-positive-light px-3 py-2 text-sm text-positive"
        role="status"
      >
        Se o e-mail estiver cadastrado, você receberá as instruções de
        redefinição.
      </div>

      <form v-else class="space-y-4" @submit.prevent="onSubmit">
        <BaseInput
          v-model="email"
          label="E-mail"
          type="email"
          placeholder="voce@exemplo.com"
          required
        />

        <p v-if="error" role="alert" class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative">
          {{ error }}
        </p>

        <BaseButton type="submit" class="w-full" :loading="loading">
          Enviar instruções
        </BaseButton>
      </form>

      <p class="mt-4 text-center text-sm text-neutral-500">
        <RouterLink to="/login" class="font-medium text-primary hover:text-primary-dark">
          Voltar para o login
        </RouterLink>
      </p>
    </div>
  </div>
</template>
