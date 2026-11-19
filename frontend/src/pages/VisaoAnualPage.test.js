import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '../services/api'
import VisaoAnualPage from './VisaoAnualPage.vue'

const routerPush = vi.hoisted(() => vi.fn())

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: {} }),
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

function annualPayload(year) {
  const months = Array.from({ length: 12 }, (_, index) => ({
    month: `${year}-${String(index + 1).padStart(2, '0')}`,
    total_income: '1000.00',
    total_fixed_expenses: '200.00',
    total_variable_expenses: '300.00',
    total_investments: '100.00',
    remaining: '400.00',
  }))
  return {
    year,
    months,
    totals: {
      total_income: '12000.00',
      total_expenses: '6000.00',
      total_investments: '1200.00',
      final_balance: '4800.00',
    },
  }
}

async function mountPage() {
  const wrapper = mount(VisaoAnualPage)
  await flushPromises()
  return wrapper
}

describe('VisaoAnualPage (navegação entre anos e visões, T-064)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.get.mockImplementation((path) => Promise.resolve(annualPayload(Number(path.split('=')[1]))))
  })

  it('consulta o ano selecionado', async () => {
    await mountPage()

    expect(api.get).toHaveBeenCalledWith('/dashboard/annual?year=2026')
  })

  it('navega entre anos pelo seletor', async () => {
    const wrapper = await mountPage()

    const yearSelect = wrapper.find('select')
    await yearSelect.setValue('2027')
    await flushPromises()

    expect(api.get).toHaveBeenCalledWith('/dashboard/annual?year=2027')
    expect(wrapper.text()).toContain('12.000,00')
  })

  it('abre a visão mensal ao clicar em um mês (alternar visão)', async () => {
    const wrapper = await mountPage()

    const januaryHeader = wrapper.findAll('th').find((header) => header.text().trim() === 'Jan')
    await januaryHeader.trigger('click')

    expect(routerPush).toHaveBeenCalledWith({
      name: 'visao-mensal',
      query: { month: '2026-01' },
    })
  })
})
