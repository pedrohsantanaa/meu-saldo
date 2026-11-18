<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseInput from '../components/BaseInput.vue'
import { api } from '../services/api'

const router = useRouter()
const route = useRoute()

const password = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''

  if (password.value !== confirm.value) {
    error.value = 'As senhas informadas não coincidem.'
    return
  }

  loading.value = true
  try {
    await api.post('/auth/reset-password', {
      token: route.query.token ?? '',
      password: password.value,
    })
    router.push({ name: 'login' })
  } catch (err) {
    error.value = err.message || 'Não foi possível redefinir a senha. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-neutral-50 p-4">
    <div class="w-full max-w-sm rounded-card border border-neutral-200 bg-white p-6 shadow-panel">
      <h1 class="mb-1 text-center text-lg">Definir nova senha</h1>
      <p class="mb-6 text-center text-sm text-neutral-500">
        Escolha uma nova senha para a sua conta.
      </p>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <BaseInput
          v-model="password"
          label="Nova senha"
          type="password"
          placeholder="Mínimo de 8 caracteres"
          hint="Use pelo menos 8 caracteres."
          required
        />
        <BaseInput
          v-model="confirm"
          label="Confirmar nova senha"
          type="password"
          placeholder="Repita a nova senha"
          required
        />

        <p v-if="error" role="alert" class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative">
          {{ error }}
        </p>

        <BaseButton type="submit" class="w-full" :loading="loading">
          Redefinir senha
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
