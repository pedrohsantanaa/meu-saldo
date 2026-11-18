import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from './auth'

function fakeResponse(payload) {
  return {
    ok: true,
    status: 200,
    json: async () => payload,
  }
}

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('login armazena o token e o usuário', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      fakeResponse({
        access_token: 'token-abc',
        token_type: 'bearer',
        expires_in: 3600,
        user: { id: 1, email: 'ana@example.com' },
      })
    )

    const store = useAuthStore()
    await store.login('ana@example.com', 'senha-forte-1')

    expect(store.isAuthenticated).toBe(true)
    expect(store.user.email).toBe('ana@example.com')
    expect(localStorage.getItem('meusaldo.token')).toBe('token-abc')
  })

  it('logout limpa a sessão mesmo quando o servidor falha', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('offline'))

    const store = useAuthStore()
    store.token = 'token-abc'
    localStorage.setItem('meusaldo.token', 'token-abc')

    await store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(localStorage.getItem('meusaldo.token')).toBeNull()
  })

  it('rejeita cadastro com erro do servidor', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 409,
      json: async () => ({
        error: { code: 'email_already_registered', message: 'Este e-mail já está cadastrado.' },
      }),
    })

    const store = useAuthStore()

    await expect(
      store.register({ name: 'Ana', email: 'ana@example.com', password: 'senha-forte-1' })
    ).rejects.toThrow('Este e-mail já está cadastrado.')
  })
})
