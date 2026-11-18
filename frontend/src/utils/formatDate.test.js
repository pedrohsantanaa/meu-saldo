import { describe, expect, it } from 'vitest'

import { formatDate } from './formatDate'

describe('formatDate', () => {
  it('formata datas ISO no padrão brasileiro', () => {
    expect(formatDate('2026-11-15')).toBe('15/11/2026')
  })

  it('retorna vazio para datas ausentes', () => {
    expect(formatDate('')).toBe('')
    expect(formatDate(null)).toBe('')
  })
})
