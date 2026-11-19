import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import BaseModal from './BaseModal.vue'

function mountModal(props) {
  return mount(BaseModal, {
    props,
    attachTo: document.body,
    slots: { default: '<p>Conteúdo do modal</p>' },
  })
}

function dialog() {
  return document.querySelector('[role="dialog"]')
}

describe('BaseModal (acessibilidade, T-066)', () => {
  it('move o foco para o diálogo ao abrir', async () => {
    const wrapper = mountModal({ open: true, title: 'Novo cartão' })
    await wrapper.vm.$nextTick()

    const panel = dialog().querySelector('div[tabindex="-1"]')
    expect(panel).not.toBeNull()
    expect(document.activeElement).toBe(panel)

    wrapper.unmount()
  })

  it('fecha com a tecla Escape', async () => {
    const wrapper = mountModal({ open: true, title: 'Novo cartão' })

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

    expect(wrapper.emitted('update:open')).toBeTruthy()
    expect(wrapper.emitted('update:open')[0]).toEqual([false])
    wrapper.unmount()
  })

  it('expõe aria-modal e rótulo acessível', () => {
    const wrapper = mountModal({ open: true, title: 'Novo cartão' })

    expect(dialog().getAttribute('aria-modal')).toBe('true')
    expect(dialog().getAttribute('aria-label')).toBe('Novo cartão')
    wrapper.unmount()
  })
})
