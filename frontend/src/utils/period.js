export function addMonths(date, count) {
  return new Date(date.getFullYear(), date.getMonth() + count, 1)
}

export function addYears(date, count) {
  return new Date(date.getFullYear() + count, date.getMonth(), 1)
}

export function formatMonthYear(date) {
  const text = date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export function formatYear(date) {
  return String(date.getFullYear())
}

export function isSameMonth(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth()
}
