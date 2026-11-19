// Indicadores de utilização do orçamento (T-058).
//
// Percentual de alerta "próximo do limite": 80% — decisão aprovada pelo
// produto (era sugestão em `design.md` §5.4; ver `spec.md` §6.13).
export const NEAR_LIMIT_PERCENT = 80

// Percentual utilizado = (Gastos / Orçamento) × 100, calculado somente
// para orçamento maior que zero (T-058). Orçamento indefinido ("Não
// definido", AC-072) ou zero não tem percentual.
export function usagePercent(row) {
  if (row.budget_amount === null || row.budget_amount === undefined) return null
  const budget = Number(row.budget_amount)
  if (budget <= 0) return null
  return Math.round((Number(row.spent) / budget) * 1000) / 10
}

// Estados: 'undefined' (Não definido), 'ok' (Dentro do orçamento),
// 'near' (Próximo do limite), 'full' (Totalmente utilizado) e 'over'
// (Ultrapassado — restante negativo, AC-071).
export function budgetStatus(row) {
  if (row.budget_amount === null || row.budget_amount === undefined) return 'undefined'
  const budget = Number(row.budget_amount)
  const spent = Number(row.spent)
  if (spent > budget) return 'over'
  if (budget > 0 && spent === budget) return 'full'
  if (budget > 0 && (spent / budget) * 100 >= NEAR_LIMIT_PERCENT) return 'near'
  return 'ok'
}

export const statusLabels = {
  undefined: 'Não definido',
  ok: 'Dentro do orçamento',
  near: 'Próximo do limite',
  full: 'Totalmente utilizado',
  over: 'Ultrapassado',
}
