import { createRouter, createWebHistory } from 'vue-router'

import CartoesPage from '../pages/CartoesPage.vue'
import CategoriasPage from '../pages/CategoriasPage.vue'
import ForgotPasswordPage from '../pages/ForgotPasswordPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import MovimentacoesPage from '../pages/MovimentacoesPage.vue'
import OrcamentosPage from '../pages/OrcamentosPage.vue'
import PlaceholderPage from '../pages/PlaceholderPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import RelatoriosPage from '../pages/RelatoriosPage.vue'
import ResetPasswordPage from '../pages/ResetPasswordPage.vue'
import VisaoAnualPage from '../pages/VisaoAnualPage.vue'
import VisaoMensalPage from '../pages/VisaoMensalPage.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { title: 'Entrar', public: true },
  },
  {
    path: '/registro',
    name: 'registro',
    component: RegisterPage,
    meta: { title: 'Criar conta', public: true },
  },
  {
    path: '/esqueci-senha',
    name: 'esqueci-senha',
    component: ForgotPasswordPage,
    meta: { title: 'Recuperar senha', public: true },
  },
  {
    path: '/redefinir-senha',
    name: 'redefinir-senha',
    component: ResetPasswordPage,
    meta: { title: 'Redefinir senha', public: true },
  },
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

router.beforeEach((to) => {
  const auth = useAuthStore()

  // T-024: rotas privadas exigem autenticação; usuários não autenticados
  // são redirecionados para o login.
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'visao-mensal' }
  }

  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · meuSaldo` : 'meuSaldo'
})

export default router
