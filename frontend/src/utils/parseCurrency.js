export function parseCurrency(text) {
  if (text === null || text === undefined) return 0

  const cleaned = String(text)
    .replace(/R\$/g, '')
    .replace(/[\s\u00a0]/g, '')

  if (!cleaned) return 0

  const hasComma = cleaned.includes(',')
  const normalized = hasComma ? cleaned.replace(/\./g, '').replace(',', '.') : cleaned
  const value = Number.parseFloat(normalized)

  return Number.isNaN(value) ? 0 : value
}
