import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { setUnauthorizedHandler } from './services/api'
import { useAuthStore } from './stores/auth'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Nunca falhar em silêncio (T-065): erros de render e de navegação
// ficam registrados no console para diagnóstico.
app.config.errorHandler = (error) => {
  console.error('[Cifaro] erro não tratado:', error)
}

router.onError((error) => {
  console.error('[Cifaro] erro de navegação:', error)
})

// Sessão expirada/revogada: limpa a sessão e leva ao login com aviso.
setUnauthorizedHandler(() => {
  const auth = useAuthStore()
  if (auth.isAuthenticated) {
    auth.clear()
    router.push({ name: 'login', query: { reason: 'expired' } })
  }
})

const auth = useAuthStore()
if (auth.isAuthenticated) {
  auth.fetchUser()
}

app.mount('#app')
