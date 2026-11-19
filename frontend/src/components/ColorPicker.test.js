import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ColorPicker from './ColorPicker.vue'
import { cardColorOptions } from '../utils/cardColors'

describe('ColorPicker', () => {
  it('exibe a grade grande de cores com rótulos acessíveis', () => {
    const wrapper = mount(ColorPicker, { props: { modelValue: 'purple' } })

    const swatches = wrapper.findAll('[role="radio"]')
    expect(swatches).toHaveLength(cardColorOptions.length)
    expect(wrapper.find('[aria-label="Turquesa"]').exists()).toBe(true)
    expect(wrapper.attributes('aria-label')).toBeUndefined()
  })

  it('destaca a cor selecionada', () => {
    const wrapper = mount(ColorPicker, { props: { modelValue: 'purple' } })

    expect(wrapper.find('[aria-label="Roxo"]').attributes('aria-checked')).toBe('true')
    expect(wrapper.find('[aria-label="Turquesa"]').attributes('aria-checked')).toBe('false')
  })

  it('emite a cor escolhida no clique', async () => {
    const wrapper = mount(ColorPicker, { props: { modelValue: 'purple' } })

    await wrapper.find('[aria-label="Turquesa"]').trigger('click')

    const [value] = wrapper.emitted('update:modelValue')[0]
    expect(value).toBe('teal')
  })
})
