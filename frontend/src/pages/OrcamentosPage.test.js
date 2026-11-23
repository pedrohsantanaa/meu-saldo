import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import BudgetSection from '../components/BudgetSection.vue'
import { api } from '../services/api'
import OrcamentosPage from './OrcamentosPage.vue'

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

const cards = [
  { id: 1, name: 'Nubank' },
  { id: 2, name: 'Inter' },
]

function mockApi(cardList = cards) {
  api.get.mockImplementation((path) => {
    if (path === '/cards') return Promise.resolve(cardList)
    return Promise.resolve([])
  })
}

async function mountPage() {
  const wrapper = mount(OrcamentosPage, {
    global: {
      stubs: {
        BudgetSection: true,
        Teleport: { template: '<div><slot /></div>' },
      },
    },
  })
  await flushPromises()
  return wrapper
}

describe('OrcamentosPage (escopo do orçamento, T-074)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApi()
  })

  it('começa no primeiro cartão e oferece despesas gerais', async () => {
    const wrapper = await mountPage()

    const section = wrapper.findComponent(BudgetSection)
    expect(section.props('mode')).toBe('card')
    expect(section.props('cardId')).toBe(1)

    const labels = wrapper
      .find('select')
      .findAll('option')
      .map((option) => option.text())
    expect(labels).toContain('Despesas gerais (sem cartão)')
    expect(labels).toContain('Nubank')
    expect(labels).toContain('Inter')
  })

  it('alterna para despesas gerais (AC-111)', async () => {
    const wrapper = await mountPage()

    await wrapper.find('select').setValue('general')
    await flushPromises()

    const section = wrapper.findComponent(BudgetSection)
    expect(section.props('mode')).toBe('general')
    expect(section.props('cardId')).toBeNull()
    expect(wrapper.text()).toContain('Defina um orçamento por categoria')
  })

  it('funciona sem cartões cadastrados, usando despesas gerais', async () => {
    mockApi([])
    const wrapper = await mountPage()

    const section = wrapper.findComponent(BudgetSection)
    expect(section.exists()).toBe(true)
    expect(section.props('mode')).toBe('general')
  })

  it('mostra erro com nova tentativa quando a API falha (AC-080)', async () => {
    api.get.mockRejectedValue(new Error('Serviço indisponível'))
    const wrapper = await mountPage()

    expect(wrapper.text()).toContain('Serviço indisponível')
    expect(wrapper.findComponent(BudgetSection).exists()).toBe(false)

    mockApi()
    await wrapper
      .findAll('button')
      .find((button) => button.text().includes('Tentar novamente'))
      .trigger('click')
    await flushPromises()

    expect(wrapper.findComponent(BudgetSection).exists()).toBe(true)
  })
})
