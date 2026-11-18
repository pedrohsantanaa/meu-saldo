import { createRouter, createWebHistory } from 'vue-router'

import VisaoGeralPage from '../pages/VisaoGeralPage.vue'
import PlaceholderPage from '../pages/PlaceholderPage.vue'

const routes = [
  {
    path: '/',
    name: 'visao-geral',
    component: VisaoGeralPage,
    meta: { title: 'Visão geral' },
  },
  {
    path: '/movimentacoes',
    name: 'movimentacoes',
    component: PlaceholderPage,
    meta: { title: 'Movimentações' },
  },
  {
    path: '/cartoes',
    name: 'cartoes',
    component: PlaceholderPage,
    meta: { title: 'Cartões' },
  },
  {
    path: '/orcamentos',
    name: 'orcamentos',
    component: PlaceholderPage,
    meta: { title: 'Orçamentos' },
  },
  {
    path: '/categorias',
    name: 'categorias',
    component: PlaceholderPage,
    meta: { title: 'Categorias' },
  },
  {
    path: '/configuracoes',
    name: 'configuracoes',
    component: PlaceholderPage,
    meta: { title: 'Configurações' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · meuSaldo` : 'meuSaldo'
})

export default router
