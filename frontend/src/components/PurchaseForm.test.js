import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import PurchaseForm from './PurchaseForm.vue'

const categories = [
  { id: 1, name: 'Alimentação', group_type: 'expense', is_active: true },
  { id: 2, name: 'Poupança', group_type: 'investment', is_active: true },
  { id: 3, name: 'Lazer', group_type: 'expense', is_active: false },
]

describe('PurchaseForm', () => {
  it('emite a compra com categoria numérica (T-047)', async () => {
    const wrapper = mount(PurchaseForm, { props: { categories } })

    await wrapper.findAll('input')[0].setValue('Mercado')
    await wrapper.find('select').setValue('1')

    await wrapper.find('form').trigger('submit')

    const [payload] = wrapper.emitted('submit')[0]
    expect(payload.description).toBe('Mercado')
    expect(payload.category_id).toBe(1)
  })

  it('lista somente categorias de despesa ativas', () => {
    const wrapper = mount(PurchaseForm, { props: { categories } })

    const options = wrapper.findAll('select option').map((option) => option.text())
    expect(options).toContain('Alimentação')
    expect(options).not.toContain('Poupança')
    expect(options).not.toContain('Lazer')
  })

  it('preenche o formulário com a categoria inicial (T-059)', async () => {
    const wrapper = mount(PurchaseForm, {
      props: {
        categories,
        initial: {
          description: 'Gasolina',
          total_amount: '80.00',
          purchase_date: '2026-11-10',
          category_id: 1,
        },
      },
    })

    expect(wrapper.findAll('input')[0].element.value).toBe('Gasolina')
    expect(wrapper.find('select').element.value).toBe('1')
  })

  it('exibe erro de salvamento', () => {
    const wrapper = mount(PurchaseForm, {
      props: { categories, error: 'Cartão inativo não aceita novas compras.' },
    })

    expect(wrapper.text()).toContain('Cartão inativo não aceita novas compras.')
  })

  it('cancela o formulário', async () => {
    const wrapper = mount(PurchaseForm, { props: { categories } })

    const cancelButton = wrapper
      .findAll('button')
      .find((button) => button.text().trim() === 'Cancelar')
    await cancelButton.trigger('click')

    expect(wrapper.emitted('cancel')).toHaveLength(1)
  })
})
