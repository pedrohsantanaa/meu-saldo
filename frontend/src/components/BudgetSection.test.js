import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '../services/api'
import BudgetSection from './BudgetSection.vue'

vi.mock('../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}))

const categories = [
  { id: 1, name: 'Alimentação', group_type: 'expense', is_active: true },
  { id: 2, name: 'Transporte/combustível', group_type: 'expense', is_active: true },
]

const summary = {
  month: '2026-11',
  card_id: 1,
  rows: [
    {
      id: 1,
      category_id: 1,
      category_name: 'Alimentação',
      budget_amount: '500.00',
      spent: '620.00',
      remaining: '-120.00',
      usage_percent: 124,
    },
    {
      id: null,
      category_id: 2,
      category_name: 'Transporte/combustível',
      budget_amount: null,
      spent: '80.00',
      remaining: null,
      usage_percent: null,
    },
  ],
  totals: { budget_amount: '500.00', spent: '700.00', remaining: '-120.00' },
}

function mockApi() {
  api.get.mockImplementation((path) => {
    if (path === '/categories') return Promise.resolve(categories)
    if (path.startsWith('/budgets')) return Promise.resolve(summary)
    return Promise.resolve([])
  })
}

async function mountSection() {
  const wrapper = mount(BudgetSection, {
    props: { cardId: 1, period: new Date(2026, 10, 1) },
  })
  await flushPromises()
  return wrapper
}

describe('BudgetSection', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApi()
  })

  it('consulta o orçamento do cartão no mês selecionado (AC-063)', async () => {
    await mountSection()

    expect(api.get).toHaveBeenCalledWith('/budgets?month=2026-11&card_id=1')
  })

  it('exibe "Não definido" para categoria sem orçamento (AC-072)', async () => {
    const wrapper = await mountSection()

    expect(wrapper.text()).toContain('Transporte/combustível')
    expect(wrapper.text()).toContain('Não definido')
    expect(wrapper.text()).toContain('80,00')
  })

  it('indica orçamento ultrapassado e exibe o totalizador (AC-071/AC-075)', async () => {
    const wrapper = await mountSection()

    expect(wrapper.text()).toContain('Ultrapassado')
    // O formato pt-BR separa "R$" do valor com espaço não separável.
    expect(wrapper.text()).toMatch(/-R\$\s120,00/)
    expect(wrapper.text()).toContain('Total')
    expect(wrapper.text()).toContain('700,00')
  })
})
