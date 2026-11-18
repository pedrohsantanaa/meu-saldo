export function formatDate(isoDate) {
  if (!isoDate) return ''
  const [year, month, day] = String(isoDate).split('-')
  return `${day}/${month}/${year}`
}
