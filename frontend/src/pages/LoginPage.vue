<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseInput from '../components/BaseInput.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect
    router.push(typeof redirect === 'string' ? redirect : { name: 'visao-mensal' })
  } catch (err) {
    error.value = err.message || 'Não foi possível entrar. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-neutral-50 p-4">
    <div class="w-full max-w-sm rounded-card border border-neutral-200 bg-white p-6 shadow-panel">
      <div class="mb-6 flex items-center justify-center gap-2">
        <svg class="h-8 w-8" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <rect x="3" y="12" width="4" height="8" rx="1" class="fill-action" />
          <rect x="10" y="8" width="4" height="12" rx="1" class="fill-action" />
          <rect x="17" y="4" width="4" height="16" rx="1" class="fill-action" />
        </svg>
        <span class="text-2xl font-semibold text-neutral-900">meuSaldo</span>
      </div>

      <h1 class="mb-1 text-center text-lg">Entrar</h1>
      <p class="mb-6 text-center text-sm text-neutral-500">
        Acesse sua conta para acompanhar suas finanças.
      </p>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <BaseInput
          v-model="email"
          label="E-mail"
          type="email"
          placeholder="voce@exemplo.com"
          required
        />
        <BaseInput
          v-model="password"
          label="Senha"
          type="password"
          placeholder="Sua senha"
          required
        />

        <p
          v-if="error"
          role="alert"
          class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
        >
          {{ error }}
        </p>

        <BaseButton type="submit" class="w-full" :loading="loading">Entrar</BaseButton>
      </form>

      <p class="mt-4 text-center text-sm text-neutral-500">
        Ainda não tem conta?
        <RouterLink to="/registro" class="font-medium text-primary hover:text-primary-dark">
          Cadastre-se
        </RouterLink>
      </p>
      <p class="mt-2 text-center text-sm text-neutral-500">
        <RouterLink to="/esqueci-senha" class="font-medium text-primary hover:text-primary-dark">
          Esqueci minha senha
        </RouterLink>
      </p>
    </div>
  </div>
</template>
