import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '../services/api'
import CartoesPage from './CartoesPage.vue'

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

const card = {
  id: 1,
  name: 'Nubank',
  issuer: 'Nubank',
  credit_limit: '5000.00',
  closing_day: 28,
  due_day: 10,
  is_active: true,
  committed_amount: '1200.00',
  available_limit: '3800.00',
  created_at: '2026-01-15T00:00:00',
}

const invoice = {
  id: 10,
  credit_card_id: 1,
  reference_month: '2026-12-01',
  closing_date: '2026-11-28',
  due_date: '2026-12-10',
  status: 'open',
  total: '1200.00',
  paid_amount: '0.00',
  open_amount: '1200.00',
}

function mockApi() {
  api.get.mockImplementation((path) => {
    if (path === '/categories') {
      return Promise.resolve([
        {
          id: 1,
          name: 'Alimentação',
          group_type: 'expense',
          expense_type: 'variable',
          is_active: true,
        },
      ])
    }
    if (path === '/cards') return Promise.resolve([card])
    if (path.startsWith('/cards/1/purchases')) {
      return Promise.resolve([
        {
          id: 5,
          credit_card_id: 1,
          category_id: 1,
          invoice_id: 10,
          description: 'Mercado',
          purchase_date: '2026-11-10',
          total_amount: '1200.00',
          installments_count: 1,
          notes: null,
          created_at: '2026-11-10T00:00:00',
        },
      ])
    }
    if (path === '/cards/1/invoices') return Promise.resolve([invoice])
    if (path === '/cards/1/invoices/overview') {
      return Promise.resolve({ current: invoice, next: null })
    }
    return Promise.resolve([])
  })
}

async function mountPage() {
  const wrapper = mount(CartoesPage)
  await flushPromises()
  return wrapper
}

describe('CartoesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApi()
  })

  it('exibe o cartão selecionado com os indicadores de limite (T-050)', async () => {
    const wrapper = await mountPage()

    expect(wrapper.text()).toContain('Cartão Nubank')
    expect(wrapper.text()).toContain('5.000,00')
    expect(wrapper.text()).toContain('1.200,00')
    expect(wrapper.text()).toContain('3.800,00')
  })

  it('lista as compras do período com fatura associada (T-047)', async () => {
    const wrapper = await mountPage()

    expect(wrapper.text()).toContain('Mercado')
    expect(wrapper.text()).toContain('Alimentação')
  })

  it('mostra fatura atual e permite registrar pagamento (T-051)', async () => {
    const wrapper = await mountPage()

    await wrapper
      .findAll('button')
      .find((button) => button.text().trim() === 'Faturas')
      .trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('12/2026')
    expect(wrapper.text()).toContain('Fatura atual')
    expect(wrapper.text()).toContain('Em aberto')
    expect(wrapper.text()).toContain('Registrar pagamento')
  })
})
