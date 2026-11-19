// Paleta de cores dos cartões (escolhida pelo usuário no formulário).
// As classes de gradiente são literais para o Tailwind gerar o CSS.
export const cardColorOptions = [
  { value: 'red', label: 'Vermelho', gradient: 'from-red-500 to-red-700' },
  { value: 'orange', label: 'Laranja', gradient: 'from-orange-500 to-orange-700' },
  { value: 'amber', label: 'Âmbar', gradient: 'from-amber-500 to-amber-700' },
  { value: 'yellow', label: 'Amarelo', gradient: 'from-yellow-500 to-yellow-700' },
  { value: 'lime', label: 'Lima', gradient: 'from-lime-500 to-lime-700' },
  { value: 'green', label: 'Verde', gradient: 'from-green-500 to-green-700' },
  { value: 'emerald', label: 'Esmeralda', gradient: 'from-emerald-500 to-emerald-700' },
  { value: 'teal', label: 'Turquesa', gradient: 'from-teal-500 to-teal-700' },
  { value: 'cyan', label: 'Ciano', gradient: 'from-cyan-500 to-cyan-700' },
  { value: 'sky', label: 'Céu', gradient: 'from-sky-500 to-sky-700' },
  { value: 'blue', label: 'Azul', gradient: 'from-blue-500 to-blue-700' },
  { value: 'indigo', label: 'Índigo', gradient: 'from-indigo-500 to-indigo-700' },
  { value: 'violet', label: 'Violeta', gradient: 'from-violet-500 to-violet-700' },
  { value: 'purple', label: 'Roxo', gradient: 'from-purple-500 to-purple-700' },
  { value: 'fuchsia', label: 'Fúcsia', gradient: 'from-fuchsia-500 to-fuchsia-700' },
  { value: 'pink', label: 'Rosa', gradient: 'from-pink-500 to-pink-700' },
  { value: 'rose', label: 'Rosé', gradient: 'from-rose-500 to-rose-700' },
  { value: 'stone', label: 'Pedra', gradient: 'from-stone-500 to-stone-700' },
  { value: 'slate', label: 'Ardósia', gradient: 'from-slate-500 to-slate-700' },
]

export const cardColorGradients = Object.fromEntries(
  cardColorOptions.map((option) => [option.value, option.gradient]),
)

// Cartões cadastrados antes do campo de cor mantêm o gradiente por id
// até serem editados.
const legacyGradients = [
  'from-purple-500 to-purple-700',
  'from-blue-500 to-blue-700',
  'from-orange-400 to-orange-600',
  'from-emerald-500 to-emerald-700',
  'from-rose-500 to-rose-700',
]

export function gradientForCard(card) {
  if (card.color && cardColorGradients[card.color]) {
    return cardColorGradients[card.color]
  }
  return legacyGradients[card.id % legacyGradients.length]
}

export function colorLabel(value) {
  return cardColorOptions.find((option) => option.value === value)?.label ?? ''
}
