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
  const wrapper = mount(CartoesPage, {
    global: {
      stubs: { Teleport: { template: '<div><slot /></div>' } },
    },
  })
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

  it('cadastra um cartão pelo formulário (AC-047)', async () => {
    api.post.mockResolvedValue(card)
    const wrapper = await mountPage()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Novo Cartão'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('input')[0].setValue('Nubank')
    await form.findAll('input')[1].setValue('Nubank')
    await form.findAll('input')[2].setValue('R$ 5.000,00')

    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/cards')
    expect(payload.name).toBe('Nubank')
    expect(payload.credit_limit).toBe(5000)
    expect(payload.closing_day).toBe(1)
    expect(payload.due_day).toBe(10)
  })

  it('cadastra um cartão com a cor escolhida no seletor (AC-047)', async () => {
    api.post.mockResolvedValue(card)
    const wrapper = await mountPage()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Novo Cartão'))
      .trigger('click')
    await flushPromises()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Escolher cor'))
      .trigger('click')
    await flushPromises()

    await wrapper.find('[aria-label="Turquesa"]').trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('input')[0].setValue('Nubank')
    await form.trigger('submit')
    await flushPromises()

    const [, payload] = api.post.mock.calls[0]
    expect(payload.color).toBe('teal')
  })

  it('registra uma compra pelo formulário (AC-053)', async () => {
    api.post.mockResolvedValue({})
    const wrapper = await mountPage()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Nova Compra'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('input')[0].setValue('Mercado')
    await form.findAll('input')[1].setValue('R$ 385,26')
    await form.find('select').setValue('1')

    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/cards/1/purchases')
    expect(payload.description).toBe('Mercado')
    expect(payload.amount ?? payload.total_amount).toBe(385.26)
    expect(payload.category_id).toBe(1)
  })
})
