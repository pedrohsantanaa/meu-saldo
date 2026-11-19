import { describe, expect, it } from 'vitest'

import { NEAR_LIMIT_PERCENT, budgetStatus, usagePercent } from './budget'

describe('budgetStatus', () => {
  it('marca categoria sem orçamento como indefinida (AC-072)', () => {
    const row = { budget_amount: null, spent: '150.00' }
    expect(budgetStatus(row)).toBe('undefined')
    expect(usagePercent(row)).toBeNull()
  })

  it('considera dentro do orçamento abaixo do limiar', () => {
    const row = { budget_amount: '500.00', spent: '250.00' }
    expect(budgetStatus(row)).toBe('ok')
  })

  it('indica próximo do limite a partir de 80%', () => {
    const row = { budget_amount: '500.00', spent: '400.00' }
    expect(NEAR_LIMIT_PERCENT).toBe(80)
    expect(budgetStatus(row)).toBe('near')
  })

  it('indica totalmente utilizado quando restante é zero (AC-070)', () => {
    const row = { budget_amount: '500.00', spent: '500.00' }
    expect(budgetStatus(row)).toBe('full')
  })

  it('indica ultrapassado quando gastos superam o orçamento (AC-071)', () => {
    const row = { budget_amount: '500.00', spent: '620.00' }
    expect(budgetStatus(row)).toBe('over')
  })

  it('não calcula percentual para orçamento zero (T-058)', () => {
    const row = { budget_amount: '0.00', spent: '0.00' }
    expect(usagePercent(row)).toBeNull()
  })
})

describe('usagePercent', () => {
  it('calcula (gastos / orçamento) × 100 com uma casa decimal', () => {
    expect(usagePercent({ budget_amount: '500.00', spent: '320.00' })).toBe(64)
    expect(usagePercent({ budget_amount: '300.00', spent: '150.00' })).toBe(50)
  })
})
