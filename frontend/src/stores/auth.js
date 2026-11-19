import { defineStore } from 'pinia'

import { api, ApiError } from '../services/api'

const TOKEN_KEY = 'meusaldo.token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY),
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },

  actions: {
    async login(email, password) {
      const data = await api.post('/auth/login', { email, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem(TOKEN_KEY, data.access_token)
    },

    async fetchUser() {
      // Recarrega o usuário autenticado (ex.: após F5). Só limpa a
      // sessão quando o servidor rejeita o token (401).
      try {
        this.user = await api.get('/auth/me')
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) this.clear()
      }
    },

    async register(payload) {
      await api.post('/auth/register', payload)
    },

    async logout() {
      try {
        await api.post('/auth/logout')
      } catch {
        // Sessão já pode estar inválida no servidor; limpa mesmo assim.
      }
      this.clear()
    },

    clear() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
