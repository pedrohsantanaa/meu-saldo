import {
  ArrowsRightLeftIcon,
  ChartPieIcon,
  CreditCardIcon,
  DocumentTextIcon,
  HomeIcon,
  Squares2X2Icon,
  TagIcon,
  WalletIcon,
} from '@heroicons/vue/24/outline'

// Navegação conforme o protótipo aprovado (docs/interface.png).
export const navItems = [
  {
    name: 'dashboard',
    title: 'Dashboard',
    icon: HomeIcon,
    children: [
      { name: 'visao-mensal', to: '/', title: 'Visão Mensal' },
      { name: 'visao-anual', to: '/anual', title: 'Visão Anual' },
    ],
  },
  {
    name: 'movimentacoes',
    to: '/movimentacoes',
    title: 'Movimentações',
    icon: ArrowsRightLeftIcon,
  },
  { name: 'cartoes', to: '/cartoes', title: 'Cartões', icon: CreditCardIcon },
  { name: 'orcamentos', to: '/orcamentos', title: 'Orçamentos', icon: ChartPieIcon },
  { name: 'categorias', to: '/categorias', title: 'Categorias', icon: TagIcon },
  { name: 'relatorios', to: '/relatorios', title: 'Relatórios', icon: DocumentTextIcon },
  {
    name: 'configuracoes',
    to: '/configuracoes',
    title: 'Configurações',
    icon: Squares2X2Icon,
  },
]

export const chartPalette = {
  green: '#16a34a',
  red: '#dc2626',
  purple: '#8b5cf6',
  orange: '#f97316',
  blue: '#2563eb',
}

export { WalletIcon }
