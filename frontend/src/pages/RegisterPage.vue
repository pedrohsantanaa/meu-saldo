<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseInput from '../components/BaseInput.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const name = ref('')
const email = ref('')
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
    await auth.register({
      name: name.value,
      email: email.value,
      password: password.value,
    })
    await auth.login(email.value, password.value)
    router.push({ name: 'visao-mensal' })
  } catch (err) {
    error.value = err.message || 'Não foi possível concluir o cadastro. Tente novamente.'
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

      <h1 class="mb-1 text-center text-lg">Criar conta</h1>
      <p class="mb-6 text-center text-sm text-neutral-500">
        Cadastre-se para organizar suas finanças.
      </p>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <BaseInput v-model="name" label="Nome" placeholder="Seu nome" required />
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
          placeholder="Mínimo de 8 caracteres"
          hint="Use pelo menos 8 caracteres."
          required
        />
        <BaseInput
          v-model="confirm"
          label="Confirmar senha"
          type="password"
          placeholder="Repita a senha"
          required
        />

        <p
          v-if="error"
          role="alert"
          class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
        >
          {{ error }}
        </p>

        <BaseButton type="submit" class="w-full" :loading="loading">Criar conta</BaseButton>
      </form>

      <p class="mt-4 text-center text-sm text-neutral-500">
        Já tem conta?
        <RouterLink to="/login" class="font-medium text-primary hover:text-primary-dark">
          Entrar
        </RouterLink>
      </p>
    </div>
  </div>
</template>
