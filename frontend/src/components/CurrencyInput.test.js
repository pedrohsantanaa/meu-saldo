import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import CurrencyInput from './CurrencyInput.vue'

const normalize = (text) => text.replace(/\u00a0/g, ' ')

describe('CurrencyInput', () => {
  it('exibe o valor formatado no padrão brasileiro', () => {
    const wrapper = mount(CurrencyInput, { props: { modelValue: 1234.56 } })
    expect(normalize(wrapper.find('input').element.value)).toBe('R$ 1.234,56')
  })

  it('emite valor numérico ao digitar e reformata ao sair do campo', async () => {
    const wrapper = mount(CurrencyInput, { props: { modelValue: 0 } })
    const input = wrapper.find('input')

    await input.setValue('1500,75')
    expect(wrapper.emitted('update:modelValue')[0][0]).toBe(1500.75)

    await input.trigger('blur')
    expect(normalize(input.element.value)).toBe('R$ 1.500,75')
  })
})
