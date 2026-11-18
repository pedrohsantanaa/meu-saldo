import { createRouter, createWebHistory } from 'vue-router'

import CartoesPage from '../pages/CartoesPage.vue'
import CategoriasPage from '../pages/CategoriasPage.vue'
import MovimentacoesPage from '../pages/MovimentacoesPage.vue'
import OrcamentosPage from '../pages/OrcamentosPage.vue'
import PlaceholderPage from '../pages/PlaceholderPage.vue'
import RelatoriosPage from '../pages/RelatoriosPage.vue'
import VisaoAnualPage from '../pages/VisaoAnualPage.vue'
import VisaoMensalPage from '../pages/VisaoMensalPage.vue'

const routes = [
  {
    path: '/',
    name: 'visao-mensal',
    component: VisaoMensalPage,
    meta: { title: 'Visão Mensal' },
  },
  {
    path: '/anual',
    name: 'visao-anual',
    component: VisaoAnualPage,
    meta: { title: 'Visão Anual' },
  },
  {
    path: '/movimentacoes',
    name: 'movimentacoes',
    component: MovimentacoesPage,
    meta: { title: 'Movimentações' },
  },
  {
    path: '/cartoes',
    name: 'cartoes',
    component: CartoesPage,
    meta: { title: 'Cartões' },
  },
  {
    path: '/orcamentos',
    name: 'orcamentos',
    component: OrcamentosPage,
    meta: { title: 'Orçamentos' },
  },
  {
    path: '/categorias',
    name: 'categorias',
    component: CategoriasPage,
    meta: { title: 'Categorias' },
  },
  {
    path: '/relatorios',
    name: 'relatorios',
    component: RelatoriosPage,
    meta: { title: 'Relatórios' },
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
