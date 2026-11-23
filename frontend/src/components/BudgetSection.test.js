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
  {
    id: 1,
    name: 'Alimentação',
    group_type: 'expense',
    expense_type: 'variable',
    is_active: true,
  },
  {
    id: 2,
    name: 'Transporte/combustível',
    group_type: 'expense',
    expense_type: 'fixed',
    is_active: true,
  },
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

async function mountSection(props = { cardId: 1, period: new Date(2026, 10, 1) }) {
  const wrapper = mount(BudgetSection, {
    props,
    global: {
      stubs: { Teleport: { template: '<div><slot /></div>' } },
    },
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

  it('mostra erro com nova tentativa quando a API falha (AC-080)', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/categories') return Promise.resolve(categories)
      return Promise.reject(new Error('Serviço indisponível'))
    })
    const wrapper = await mountSection()

    expect(wrapper.text()).toContain('Serviço indisponível')
    expect(wrapper.text()).toContain('Tentar novamente')

    api.get.mockImplementation((path) => {
      if (path === '/categories') return Promise.resolve(categories)
      return Promise.resolve(summary)
    })
    const retry = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Tentar novamente'))
    await retry.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('Serviço indisponível')
    expect(wrapper.text()).toContain('Alimentação')
  })

  it('cria um orçamento pelo formulário (AC-064/AC-068)', async () => {
    api.post.mockResolvedValue({
      id: 5,
      category_id: 1,
      category_name: 'Alimentação',
      budget_amount: '400.00',
      spent: '0.00',
      remaining: '400.00',
      usage_percent: 0,
    })
    const wrapper = await mountSection()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Novo Orçamento'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.find('select').setValue('1')
    await form.find('input').setValue('R$ 400,00')

    // Após salvar, o recarregamento passa a exibir o novo orçamento.
    api.get.mockImplementation((path) => {
      if (path === '/categories') return Promise.resolve(categories)
      if (path.startsWith('/budgets')) {
        return Promise.resolve({
          month: '2026-11',
          card_id: 1,
          rows: [
            {
              id: 5,
              category_id: 1,
              category_name: 'Alimentação',
              budget_amount: '400.00',
              spent: '0.00',
              remaining: '400.00',
              usage_percent: 0,
            },
          ],
          totals: { budget_amount: '400.00', spent: '0.00', remaining: '400.00' },
        })
      }
      return Promise.resolve([])
    })

    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/budgets')
    expect(payload.card_id).toBe(1)
    expect(payload.month).toBe('2026-11')
    expect(payload.category_id).toBe(1)
    expect(payload.budget_amount).toBe(400)
    // O restante planejado aparece após o recarregamento.
    expect(wrapper.text()).toContain('400,00')
  })

  it('consulta e cria orçamento geral sem cartão (AC-111)', async () => {
    const wrapper = await mountSection({
      mode: 'general',
      period: new Date(2026, 10, 1),
    })

    expect(api.get).toHaveBeenCalledWith('/budgets/general?month=2026-11')
    expect(wrapper.text()).toContain('movimentações comuns')
    // Cada categoria mostra a classificação fixa/variável (T-074).
    expect(wrapper.text()).toContain('Fixa')
    expect(wrapper.text()).toContain('Variável')

    api.post.mockResolvedValue({
      id: 9,
      category_id: 1,
      category_name: 'Alimentação',
      budget_amount: '300.00',
      spent: '0.00',
      remaining: '300.00',
      usage_percent: 0,
    })
    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Novo Orçamento'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.find('select').setValue('1')
    await form.find('input').setValue('R$ 300,00')
    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/budgets/general')
    expect(payload.card_id).toBeUndefined()
    expect(payload.month).toBe('2026-11')
    expect(payload.category_id).toBe(1)
    expect(payload.budget_amount).toBe(300)
  })

  it('lança movimentação comum pela categoria orçada (AC-112)', async () => {
    const wrapper = await mountSection({
      mode: 'general',
      period: new Date(2026, 10, 1),
    })

    api.post.mockResolvedValue({ id: 3 })
    await wrapper
      .findAll('button')
      .find(
        (button) => button.attributes('aria-label') === 'Adicionar movimentação',
      )
      .trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Nova movimentação — Alimentação')

    const form = wrapper.find('form')
    await form.findAll('input')[0].setValue('Feira do bairro')
    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/transactions')
    expect(payload.type).toBe('expense')
    expect(payload.category_id).toBe(1)
  })

  it('cria série parcelada pelo formulário (AC-116)', async () => {
    const wrapper = await mountSection()
    api.post.mockResolvedValue({
      recurrence: {
        id: 7,
        mode: 'installments',
        amount: '600.00',
        count: 3,
        start_month: '2026-11',
      },
      months: ['2026-11', '2026-12', '2027-01'],
      rows: [],
    })

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Novo Orçamento'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('select')[0].setValue('1')
    await form.findAll('select')[1].setValue('installments')
    await form.findAll('input')[0].setValue('R$ 600,00')
    await form.findAll('input')[1].setValue('3')
    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/budgets/recurrences')
    expect(payload.card_id).toBe(1)
    expect(payload.month).toBe('2026-11')
    expect(payload.recurrence).toEqual({
      mode: 'installments',
      amount: 600,
      count: 3,
    })
    // Confirmação com o intervalo de meses gerado (AC-116).
    expect(wrapper.text()).toContain('Orçamento criado para 3 meses')
  })

  it('repete o valor mensal por N meses (AC-117)', async () => {
    const wrapper = await mountSection()
    api.post.mockResolvedValue({
      recurrence: {
        id: 8,
        mode: 'monthly',
        amount: '300.00',
        count: 12,
        start_month: '2026-11',
      },
      months: ['2026-11', '2026-12', '2027-01'],
      rows: [],
    })

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Novo Orçamento'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('select')[0].setValue('1')
    await form.findAll('select')[1].setValue('monthly')
    await form.findAll('input')[0].setValue('R$ 300,00')
    await form.findAll('input')[1].setValue('12')

    // O resumo mostra o total planejado antes de salvar.
    expect(wrapper.text()).toContain('3.600,00')

    await form.trigger('submit')
    await flushPromises()

    const [path, payload] = api.post.mock.calls[0]
    expect(path).toBe('/budgets/recurrences')
    expect(payload.recurrence).toEqual({
      mode: 'monthly',
      amount: 300,
      count: 12,
    })
  })

  it('valida o número de meses da série no formulário', async () => {
    const wrapper = await mountSection()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Novo Orçamento'))
      .trigger('click')
    await flushPromises()

    const form = wrapper.find('form')
    await form.findAll('select')[1].setValue('installments')
    await form.findAll('input')[1].setValue('1')
    await form.trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Informe um número de meses entre 2 e 60.')
    expect(api.post).not.toHaveBeenCalled()
  })

  it('exibe o badge da série e exclui a série inteira (AC-119)', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/categories') return Promise.resolve(categories)
      if (path.startsWith('/budgets')) {
        return Promise.resolve({
          month: '2026-11',
          card_id: 1,
          rows: [
            {
              id: 4,
              category_id: 1,
              category_name: 'Alimentação',
              budget_amount: '200.00',
              spent: '0.00',
              remaining: '200.00',
              usage_percent: 0,
              recurrence: { id: 7, mode: 'installments', position: 2, total: 6 },
            },
          ],
          totals: { budget_amount: '200.00', spent: '0.00', remaining: '200.00' },
        })
      }
      return Promise.resolve([])
    })
    api.delete.mockResolvedValue(null)
    const wrapper = await mountSection()

    // AC-120: a linha indica a posição na série.
    expect(wrapper.text()).toContain('Parcela 2/6')

    await wrapper
      .findAll('button')
      .find((button) => button.attributes('aria-label') === 'Excluir série')
      .trigger('click')
    await flushPromises()

    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Excluir série'))
      .trigger('click')
    await flushPromises()

    expect(api.delete).toHaveBeenCalledWith('/budgets/recurrences/7')
  })
})
