import { describe, expect, it } from 'vitest'

import { addMonths, addYears, formatMonthYear, formatYear, isSameMonth } from './period'

describe('period', () => {
  it('addMonths atravessa o fim do ano', () => {
    const date = addMonths(new Date(2026, 11, 1), 1)
    expect(date.getFullYear()).toBe(2027)
    expect(date.getMonth()).toBe(0)
  })

  it('addYears preserva o mês', () => {
    const date = addYears(new Date(2026, 5, 1), -2)
    expect(date.getFullYear()).toBe(2024)
    expect(date.getMonth()).toBe(5)
  })

  it('formatMonthYear formata em português', () => {
    expect(formatMonthYear(new Date(2026, 10, 1))).toBe('Novembro de 2026')
  })

  it('formatYear retorna o ano', () => {
    expect(formatYear(new Date(2026, 10, 1))).toBe('2026')
  })

  it('isSameMonth compara mês e ano', () => {
    expect(isSameMonth(new Date(2026, 10, 5), new Date(2026, 10, 20))).toBe(true)
    expect(isSameMonth(new Date(2026, 10, 5), new Date(2026, 9, 5))).toBe(false)
  })
})
