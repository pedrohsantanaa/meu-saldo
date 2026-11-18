import { describe, expect, it } from 'vitest'

import { formatCurrency } from './formatCurrency'

describe('formatCurrency', () => {
  it('formata valores no padrão brasileiro', () => {
    expect(formatCurrency(1234.56).replace(/\u00a0/g, ' ')).toBe('R$ 1.234,56')
  })

  it('formata zero e valores ausentes como R$ 0,00', () => {
    expect(formatCurrency(0).replace(/\u00a0/g, ' ')).toBe('R$ 0,00')
    expect(formatCurrency(undefined).replace(/\u00a0/g, ' ')).toBe('R$ 0,00')
  })
})
