export function addMonths(date, count) {
  return new Date(date.getFullYear(), date.getMonth() + count, 1)
}

export function addYears(date, count) {
  return new Date(date.getFullYear() + count, date.getMonth(), 1)
}

export function formatMonthYear(date) {
  const month = date.toLocaleDateString('pt-BR', { month: 'long' })
  const capitalized = month.charAt(0).toUpperCase() + month.slice(1)
  return `${capitalized}/${date.getFullYear()}`
}

export function formatYear(date) {
  return String(date.getFullYear())
}

export function isSameMonth(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth()
}
