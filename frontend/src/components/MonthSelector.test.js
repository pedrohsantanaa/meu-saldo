import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import MonthSelector from './MonthSelector.vue'

describe('MonthSelector', () => {
  it('exibe o período no formato do protótipo (Mês/AAAA)', () => {
    const wrapper = mount(MonthSelector, {
      props: { modelValue: new Date(2026, 10, 1) },
    })
    expect(wrapper.text()).toContain('Novembro/2026')
  })

  it('avança um mês', async () => {
    const wrapper = mount(MonthSelector, {
      props: { modelValue: new Date(2026, 10, 1) },
    })

    await wrapper.find('button[aria-label="Próximo mês"]').trigger('click')

    const [next] = wrapper.emitted('update:modelValue')[0]
    expect(next.getFullYear()).toBe(2026)
    expect(next.getMonth()).toBe(11)
  })

  it('volta um mês', async () => {
    const wrapper = mount(MonthSelector, {
      props: { modelValue: new Date(2026, 10, 1) },
    })

    await wrapper.find('button[aria-label="Mês anterior"]').trigger('click')

    const [next] = wrapper.emitted('update:modelValue')[0]
    expect(next.getFullYear()).toBe(2026)
    expect(next.getMonth()).toBe(9)
  })

  it('exibe o botão Hoje apenas fora do mês atual', () => {
    const now = new Date()
    const current = mount(MonthSelector, {
      props: { modelValue: new Date(now.getFullYear(), now.getMonth(), 1) },
    })
    expect(current.text()).not.toContain('Hoje')

    const past = mount(MonthSelector, {
      props: { modelValue: new Date(2020, 0, 1) },
    })
    expect(past.text()).toContain('Hoje')
  })
})
