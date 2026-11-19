import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('./services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
  setUnauthorizedHandler: vi.fn(),
}))

import App from './App.vue'
import { createAppRouter } from './router'
import { api } from './services/api'
import { useAuthStore } from './stores/auth'

const monthlySummary = {
  month: '2026-11',
  total_income: '0.00',
  total_fixed_expenses: '0.00',
  total_variable_expenses: '0.00',
  total_investments: '0.00',
  total_outflows: '0.00',
  remaining: '0.00',
  card_purchases_total: '0.00',
  income_items: [],
  fixed_expense_items: [],
  variable_expense_items: [],
  investments_items: [],
  recent_transactions: [],
  expenses_by_category: [],
  trend: [],
}

function mockApi() {
  api.get.mockImplementation((path) => {
    if (path.startsWith('/dashboard/monthly')) {
      return Promise.resolve(monthlySummary)
    }
    if (path.startsWith('/dashboard/annual')) {
      return Promise.resolve({
        year: 2026,
        months: Array.from({ length: 12 }, (_, index) => ({
          month: `2026-${String(index + 1).padStart(2, '0')}`,
          total_income: '0.00',
          total_fixed_expenses: '0.00',
          total_variable_expenses: '0.00',
          total_investments: '0.00',
          remaining: '0.00',
        })),
        totals: {
          total_income: '0.00',
          total_expenses: '0.00',
          total_investments: '0.00',
          final_balance: '0.00',
        },
      })
    }
    return Promise.resolve([])
  })
}

let pinia
let router

async function mountApp() {
  const wrapper = mount(App, {
    global: { plugins: [pinia, router] },
  })
  await router.isReady()
  await flushPromises()
  return wrapper
}

const menu = [
  { label: 'Visão Mensal', name: 'visao-mensal', heading: 'Visão Mensal' },
  { label: 'Visão Anual', name: 'visao-anual', heading: 'Visão Anual' },
  { label: 'Movimentações', name: 'movimentacoes', heading: 'Movimentações' },
  { label: 'Cartões', name: 'cartoes', heading: 'Cartões' },
  { label: 'Orçamentos', name: 'orcamentos', heading: 'Orçamentos' },
  { label: 'Categorias', name: 'categorias', heading: 'Categorias' },
  { label: 'Relatórios', name: 'relatorios', heading: 'Relatórios' },
]

describe('Navegação pelo menu (regressão)', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    mockApi()
    // Router e Pinia próprios por teste: o guard resolve o store do app
    // que instalou o router, então singletons vazariam entre testes.
    router = createAppRouter()
    pinia = createPinia()
    setActivePinia(pinia)
    localStorage.setItem('meusaldo.token', 'token-de-teste')
    await router.push('/')
    await flushPromises()
  })

  it('alterna de página ao clicar em cada item do menu', async () => {
    const wrapper = await mountApp()

    for (const item of menu) {
      const link = wrapper.findAll('a').find((anchor) => anchor.text().trim() === item.label)
      expect(link, `link "${item.label}" existe`).toBeTruthy()

      await link.trigger('click')
      await flushPromises()

      // A rota E o conteúdo renderizado mudam (não apenas a URL).
      expect(router.currentRoute.value.name).toBe(item.name)
      expect(wrapper.find('h1').text()).toBe(item.heading)
    }
  })

  it('mantém a rota atualizada ao voltar e avançar do histórico', async () => {
    const wrapper = await mountApp()

    const movimentacoes = wrapper
      .findAll('a')
      .find((anchor) => anchor.text().trim() === 'Movimentações')
    await movimentacoes.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('movimentacoes')

    const popped = new Promise((resolve) =>
      window.addEventListener('popstate', resolve, { once: true }),
    )
    router.back()
    await popped
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('visao-mensal')
    expect(wrapper.find('h1').text()).toBe('Visão Mensal')
  })

  it('redireciona para o login sem sessão, com aviso', async () => {
    // O app montado instala o router; o guard resolve o Pinia dele.
    await mountApp()
    localStorage.removeItem('meusaldo.token')
    useAuthStore(pinia).clear()
    await router.push('/movimentacoes')
    await flushPromises()

    const wrapper = await mountApp()

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/movimentacoes')
    expect(wrapper.find('h1').text()).toBe('Entrar')
    expect(wrapper.text()).toContain('Faça login para continuar.')
  })

  it('exibe aviso de sessão expirada', async () => {
    await mountApp()
    localStorage.removeItem('meusaldo.token')
    useAuthStore(pinia).clear()
    await router.push({ name: 'login', query: { reason: 'expired' } })
    await flushPromises()

    const wrapper = await mountApp()

    expect(wrapper.find('h1').text()).toBe('Entrar')
    expect(wrapper.text()).toContain('Sua sessão expirou. Faça login novamente.')
  })
})
