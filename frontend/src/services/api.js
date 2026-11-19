const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const TOKEN_KEY = 'meusaldo.token'

export class ApiError extends Error {
  constructor(code, message, status, details = null) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
  }
}

// Sessão expirada/revogada (T-065): o handler global limpa a sessão e
// redireciona ao login. Registrado em `main.js` para evitar import
// circular com o store de autenticação.
let unauthorizedHandler = null

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler
}

async function request(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY)
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  if (!response.ok) {
    let payload = null
    try {
      payload = await response.json()
    } catch {
      // Corpo não é JSON; usa o erro padrão abaixo.
    }
    const error = payload?.error ?? {}
    const apiError = new ApiError(
      error.code ?? 'request_failed',
      error.message ?? `A requisição falhou com status ${response.status}.`,
      response.status,
      error.details ?? null,
    )
    // 401 fora das rotas de autenticação = sessão inválida/expirada.
    if (apiError.status === 401 && !path.startsWith('/auth')) {
      unauthorizedHandler?.()
    }
    throw apiError
  }

  return response.status === 204 ? null : response.json()
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  patch: (path, body) => request(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: 'DELETE' }),
}
