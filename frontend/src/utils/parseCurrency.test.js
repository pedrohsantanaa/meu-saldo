import { describe, expect, it } from 'vitest'

import { parseCurrency } from './parseCurrency'

describe('parseCurrency', () => {
  it('interpreta o formato brasileiro', () => {
    expect(parseCurrency('R$ 1.234,56')).toBe(1234.56)
  })

  it('interpreta formato com ponto decimal', () => {
    expect(parseCurrency('1234.56')).toBe(1234.56)
  })

  it('retorna 0 para valores vazios ou inválidos', () => {
    expect(parseCurrency('')).toBe(0)
    expect(parseCurrency('abc')).toBe(0)
    expect(parseCurrency(null)).toBe(0)
    expect(parseCurrency(undefined)).toBe(0)
  })
})
