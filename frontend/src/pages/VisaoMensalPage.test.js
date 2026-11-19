import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: {} }),
  useRouter: () => ({ push: vi.fn() }),
}))

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

import { api } from '../services/api'
import VisaoMensalPage from './VisaoMensalPage.vue'

const monthlySummary = {
  month: '2026-11',
  total_income: '5000.00',
  total_fixed_expenses: '2000.00',
  total_variable_expenses: '800.00',
  total_investments: '400.00',
  total_outflows: '3200.00',
  remaining: '1800.00',
  card_purchases_total: '300.00',
  income_items: [{ name: 'Salário', total: '5000.00' }],
  fixed_expense_items: [],
  variable_expense_items: [],
  investments_items: [],
  recent_transactions: [],
  expenses_by_category: [],
  trend: [],
}

describe('VisaoMensalPage (estado de erro, AC-080)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('mostra mensagem de erro e nova tentativa quando a API falha', async () => {
    api.get.mockRejectedValueOnce(new Error('Serviço indisponível'))

    const wrapper = mount(VisaoMensalPage)
    await flushPromises()

    // Nunca spinner eterno: o erro fica visível com ação de retry.
    expect(wrapper.text()).toContain('Serviço indisponível')
    expect(wrapper.text()).toContain('Tentar novamente')
    expect(wrapper.text()).not.toContain('Composição das Despesas')
  })

  it('recarrega os dados ao tentar novamente', async () => {
    api.get.mockRejectedValueOnce(new Error('Serviço indisponível'))
    const wrapper = mount(VisaoMensalPage)
    await flushPromises()

    api.get.mockResolvedValueOnce(monthlySummary)
    const retry = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Tentar novamente'))
    await retry.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('Serviço indisponível')
    expect(wrapper.find('h1').text()).toBe('Visão Mensal')
    expect(wrapper.text()).toContain('5.000,00')
    expect(api.get).toHaveBeenCalledTimes(2)
  })
})
