const TOKEN_KEY = 'sv_token'
const REFRESH_TOKEN_KEY = 'sv_refresh_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setTokens(accessToken: string, refreshToken?: string): void {
  localStorage.setItem(TOKEN_KEY, accessToken)
  if (refreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  if (isRefreshing && refreshPromise) return refreshPromise

  isRefreshing = true
  refreshPromise = (async () => {
    try {
      const res = await fetch('/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      if (!res.ok) return false
      const refreshContentType = res.headers.get('content-type') || ''
      if (!refreshContentType.includes('application/json')) return false
      let data: any
      try {
        data = await res.json()
      } catch {
        return false
      }
      setTokens(data.access_token, data.refresh_token)
      return true
    } catch {
      return false
    } finally {
      isRefreshing = false
      refreshPromise = null
    }
  })()

  return refreshPromise
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  // Public auth endpoints (login, register, refresh) don't need auth header
  const PUBLIC_AUTH_PATHS = ['/auth/login', '/auth/register', '/auth/refresh']
  const isPublicAuthEndpoint = PUBLIC_AUTH_PATHS.some(
    (prefix) => path === prefix || path.startsWith(prefix + '?')
  )
  if (token && !isPublicAuthEndpoint) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(path, { ...options, headers }).catch((err) => {
    throw new ApiError(0, err instanceof DOMException && err.name === 'AbortError' ? 'La petición tomó demasiado tiempo. Inténtalo nuevamente.' : 'No se pudo conectar al servidor')
  })

  // Public auth endpoints (login/register/refresh) manage their own auth state —
  // don't intercept their 401s with auto-refresh; let the real error through.
  if (res.status === 401 && !isPublicAuthEndpoint) {
    const refreshed = await tryRefreshToken()
    if (refreshed) {
       const newToken = getToken()
       headers['Authorization'] = `Bearer ${newToken}`
       const retryRes = await fetch(path, { ...options, headers })
       if (retryRes.status === 204) return null as T
       const retryContentType = retryRes.headers.get('content-type') || ''
       let retryData: any
       if (retryContentType.includes('application/json')) {
         try {
           retryData = await retryRes.json()
         } catch {
           retryData = {}
         }
       } else {
         retryData = {}
       }
       if (!retryRes.ok) {
         const msg = retryData.detail?.[0]?.msg || retryData.detail || `Error del servidor (${retryRes.status})`
         throw new ApiError(retryRes.status, msg)
       }
       return retryData as T
    }
    clearToken()
    window.dispatchEvent(new CustomEvent('sv:unauthorized'))
    throw new ApiError(401, 'Sesión expirada')
  }

   if (res.status === 204) return null as T
   let data: T
   const contentType = res.headers.get('content-type') || ''
   if (contentType.includes('application/json')) {
     try {
       data = await res.json()
     } catch {
       data = {} as T
     }
   } else {
     data = {} as T
   }
   if (!res.ok) {
     const msg = (data as any)?.detail?.[0]?.msg || (data as any)?.detail || `Error del servidor (${res.status})`
     throw new ApiError(res.status, msg)
   }
   return data as T
}

// ── Offline queue (Zustand-backed) ──
import { useOfflineStore } from '../store/offlineStore'

export async function addToOfflineQueue(entry: { path: string; method: string; body: unknown }): Promise<void> {
  useOfflineStore.getState().add(entry)
}

export async function processOfflineQueue(): Promise<void> {
  const { queue, remove } = useOfflineStore.getState()
  if (!queue.length) return

  const failed: string[] = []
  for (const entry of queue) {
    try {
      await api(entry.path, { method: entry.method, body: JSON.stringify(entry.body) })
      remove(entry.id)
    } catch {
      failed.push(entry.id)
    }
  }
}

export async function getOfflineQueueSize(): Promise<number> {
  return useOfflineStore.getState().size()
}
