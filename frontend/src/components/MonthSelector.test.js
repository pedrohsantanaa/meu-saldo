import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import MonthSelector from './MonthSelector.vue'

describe('MonthSelector', () => {
  it('avança um mês no modo mensal', async () => {
    const wrapper = mount(MonthSelector, {
      props: { modelValue: new Date(2026, 10, 1), mode: 'mensal' },
    })

    await wrapper.find('button[aria-label="Próximo mês"]').trigger('click')

    const [next] = wrapper.emitted('update:modelValue')[0]
    expect(next.getFullYear()).toBe(2026)
    expect(next.getMonth()).toBe(11)
  })

  it('volta um ano no modo anual', async () => {
    const wrapper = mount(MonthSelector, {
      props: { modelValue: new Date(2026, 10, 1), mode: 'anual' },
    })

    await wrapper.find('button[aria-label="Ano anterior"]').trigger('click')

    const [next] = wrapper.emitted('update:modelValue')[0]
    expect(next.getFullYear()).toBe(2025)
  })

  it('alterna entre as visualizações mensal e anual', async () => {
    const wrapper = mount(MonthSelector, {
      props: { modelValue: new Date(2026, 10, 1), mode: 'mensal' },
    })

    const anual = wrapper.findAll('button').find((button) => button.text() === 'Anual')
    await anual.trigger('click')

    expect(wrapper.emitted('update:mode')[0]).toEqual(['anual'])
  })
})
