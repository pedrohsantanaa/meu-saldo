import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '../services/api'
import MovimentacoesPage from './MovimentacoesPage.vue'

const routeQuery = vi.hoisted(() => ({}))
const routerPush = vi.hoisted(() => vi.fn())

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
  useRouter: () => ({ push: routerPush }),
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

const categories = [
  { id: 1, name: 'Salário', group_type: 'income', is_active: true },
  { id: 2, name: 'Alimentação', group_type: 'expense', expense_type: 'variable', is_active: true },
]

function mockApi() {
  api.get.mockImplementation((path) => {
    if (path === '/categories') return Promise.resolve(categories)
    if (path === '/cards') return Promise.resolve([])
    if (path.startsWith('/movements')) return Promise.resolve([])
    if (path.startsWith('/transactions')) return Promise.resolve([])
    return Promise.resolve([])
  })
  api.post.mockResolvedValue({})
}

async function mountPage() {
  const wrapper = mount(MovimentacoesPage, {
    global: {
      stubs: { Teleport: { template: '<div><slot /></div>' } },
    },
  })
  await flushPromises()
  return wrapper
}

async function openForm(wrapper) {
  const button = wrapper.findAll('button').find((item) => item.text().includes('Nova Movimentação'))
  await button.trigger('click')
  await flushPromises()
}

describe('MovimentacoesPage (fluxos essenciais, T-064)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApi()
  })

  it('registra uma receita pelo formulário', async () => {
    const wrapper = await mountPage()
    await openForm(wrapper)

    const form = wrapper.find('form')
    await form.findAll('select')[0].setValue('income')
    await form.findAll('input')[0].setValue('Salário')
    await form.findAll('input')[1].setValue('R$ 7.175,09')
    await form.findAll('select')[1].setValue('1')

    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/transactions')
    expect(payload.type).toBe('income')
    expect(payload.description).toBe('Salário')
    expect(payload.amount).toBe(7175.09)
    expect(payload.category_id).toBe(1)
  })

  it('registra uma despesa com classificação e forma de pagamento', async () => {
    const wrapper = await mountPage()
    await openForm(wrapper)

    const form = wrapper.find('form')
    await form.findAll('input')[0].setValue('Mercado')
    await form.findAll('input')[1].setValue('R$ 385,26')
    await form.findAll('select')[1].setValue('2')

    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/transactions')
    expect(payload.type).toBe('expense')
    expect(payload.expense_type).toBe('variable')
    expect(payload.payment_method).toBe('pix')
    expect(payload.amount).toBe(385.26)
    expect(payload.category_id).toBe(2)
  })

  it('registra compra no cartão pela tela de movimentações (AC-121)', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/categories') return Promise.resolve(categories)
      if (path === '/cards') return Promise.resolve([{ id: 5, name: 'Nubank' }])
      return Promise.resolve([])
    })
    api.post.mockResolvedValue({
      id: 9,
      credit_card_id: 5,
      invoice_id: 2,
      invoice_reference_month: '2026-12-01',
    })
    const wrapper = await mountPage()

    const openButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Nova Compra no Cartão'))
    await openButton.trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('select')[0].setValue('5')
    await form.findAll('select')[1].setValue('2')
    await form.findAll('input')[0].setValue('Mercado')
    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/cards/5/purchases')
    // O cartão vai na URL; o corpo segue o schema de compra.
    expect('card_id' in payload).toBe(false)
    expect(payload.description).toBe('Mercado')
    expect(payload.category_id).toBe(2)

    // Confirmação com a fatura em que a compra entra (AC-121).
    expect(wrapper.text()).toContain(
      'Compra registrada na fatura de Dezembro/2026 do cartão Nubank',
    )

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Ver em Cartões'))
      .trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/cartoes')
  })

  it('compra no cartão não vira movimentação comum (AC-122)', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/categories') return Promise.resolve(categories)
      if (path === '/cards') return Promise.resolve([{ id: 5, name: 'Nubank' }])
      return Promise.resolve([])
    })
    api.post.mockResolvedValue({
      id: 9,
      credit_card_id: 5,
      invoice_id: 2,
      invoice_reference_month: '2026-12-01',
    })
    const wrapper = await mountPage()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Nova Compra no Cartão'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('select')[0].setValue('5')
    await form.findAll('select')[1].setValue('2')
    await form.trigger('submit')
    await flushPromises()

    // AC-122: o único POST é a compra no cartão — nunca /transactions.
    expect(api.post).toHaveBeenCalledTimes(1)
    expect(api.post.mock.calls[0][0]).toBe('/cards/5/purchases')
  })

  const transactionRow = {
    id: 1,
    source: 'transaction',
    transaction_date: '2026-11-12',
    description: 'Mercado',
    amount: '80.00',
    category_id: 2,
    notes: null,
    type: 'expense',
    expense_type: 'variable',
    payment_method: 'pix',
  }

  const purchaseRow = {
    id: 9,
    source: 'card_purchase',
    transaction_date: '2026-11-10',
    description: 'Farmácia',
    amount: '150.00',
    category_id: 2,
    notes: null,
    type: 'expense',
    expense_type: 'variable',
    credit_card_id: 5,
    card_name: 'Nubank',
    invoice_reference_month: '2026-12',
  }

  function mockMovements(items) {
    api.get.mockImplementation((path) => {
      if (path === '/categories') return Promise.resolve(categories)
      if (path === '/cards') return Promise.resolve([{ id: 5, name: 'Nubank' }])
      if (path.startsWith('/movements')) return Promise.resolve(items)
      return Promise.resolve([])
    })
  }

  it('lista compras no cartão identificadas pelo cartão e pela fatura (T-083)', async () => {
    mockMovements([transactionRow, purchaseRow])
    const wrapper = await mountPage()

    expect(wrapper.text()).toContain('Mercado')
    expect(wrapper.text()).toContain('Farmácia')
    // Identificação clara: tipo "Compra no cartão", cartão e fatura.
    expect(wrapper.text()).toContain('Compra no cartão')
    expect(wrapper.text()).toContain('Nubank')
    expect(wrapper.text()).toContain('Fatura de Dezembro/2026')
  })

  it('filtra por "Cartão de crédito" e por cartão utilizado', async () => {
    mockMovements([purchaseRow])
    const wrapper = await mountPage()
    const paramsOf = (call) => new URLSearchParams(call.split('?')[1])

    // O mês é filtrado pela data da compra/movimentação (mês corrente).
    const today = new Date()
    const currentMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
    expect(paramsOf(api.get.mock.calls.at(-1)[0]).get('date_from')).toBe(`${currentMonth}-01`)

    await wrapper.findAll('select')[2].setValue('credito')
    await flushPromises()
    expect(paramsOf(api.get.mock.calls.at(-1)[0]).get('payment_method')).toBe('credito')

    await wrapper.findAll('select')[3].setValue('5')
    await flushPromises()
    expect(paramsOf(api.get.mock.calls.at(-1)[0]).get('card_id')).toBe('5')

    await wrapper.findAll('select')[0].setValue('card_purchase')
    await flushPromises()
    expect(paramsOf(api.get.mock.calls.at(-1)[0]).get('type')).toBe('card_purchase')
  })

  it('edita uma compra pela lista pelo fluxo de compra', async () => {
    mockMovements([purchaseRow])
    const wrapper = await mountPage()

    await wrapper
      .findAll('button')
      .find((button) => button.attributes('aria-label') === 'Editar')
      .trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Editar compra no cartão — Nubank')
    const form = wrapper.find('form')
    await form.find('input').setValue('Farmácia populosa')
    await form.trigger('submit')
    await flushPromises()

    // Edição respeita o fluxo de compra: PUT em /cards/.../purchases/...
    const [path, payload] = api.put.mock.calls[0]
    expect(path).toBe('/cards/5/purchases/9')
    expect('card_id' in payload).toBe(false)
    expect(payload.description).toBe('Farmácia populosa')
  })

  it('exclui uma compra pelo fluxo de compra', async () => {
    mockMovements([purchaseRow])
    api.delete.mockResolvedValue(null)
    const wrapper = await mountPage()

    await wrapper
      .findAll('button')
      .find((button) => button.attributes('aria-label') === 'Excluir')
      .trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Excluir compra no cartão')
    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Excluir'))
      .trigger('click')
    await flushPromises()

    expect(api.delete).toHaveBeenCalledWith('/cards/5/purchases/9')
  })
})
