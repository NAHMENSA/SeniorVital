import { describe, it, expect, beforeEach, vi } from 'vitest'
import { getToken, setToken, clearToken, getRefreshToken, setTokens, ApiError, api } from '../api'

describe('Token management', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('setToken stores token in localStorage', () => {
    setToken('test-token')
    expect(localStorage.getItem('sv_token')).toBe('test-token')
  })

  it('getToken retrieves stored token', () => {
    localStorage.setItem('sv_token', 'my-token')
    expect(getToken()).toBe('my-token')
  })

  it('clearToken removes all auth tokens', () => {
    localStorage.setItem('sv_token', 'token')
    localStorage.setItem('sv_refresh_token', 'refresh')
    clearToken()
    expect(localStorage.getItem('sv_token')).toBeNull()
    expect(localStorage.getItem('sv_refresh_token')).toBeNull()
  })

  it('setTokens stores both access and refresh tokens', () => {
    setTokens('access-123', 'refresh-456')
    expect(getToken()).toBe('access-123')
    expect(getRefreshToken()).toBe('refresh-456')
  })

   it('ApiError has correct status and message', () => {
     const err = new ApiError(404, 'Not found')
     expect(err.status).toBe(404)
     expect(err.message).toBe('Not found')
     expect(err.name).toBe('ApiError')
   })
 })

 describe('api function', () => {
   beforeEach(() => {
     localStorage.clear()
     vi.restoreAllMocks()
   })

  it('auth endpoints do not send Authorization header', async () => {
      setToken('stale-token')
      let capturedHeaders: HeadersInit | undefined
      vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
        status: 200,
        headers: { get: () => 'application/json' },
        json: () => Promise.resolve({ ok: true }),
      } as any))
      ;(globalThis.fetch as any).mockImplementation(async (url: string, opts: any) => {
        capturedHeaders = opts.headers
        return {
          status: 200,
          headers: { get: () => 'application/json' },
          json: () => Promise.resolve({ ok: true }),
        } as any
      })

      await api('/auth/login', { method: 'POST', body: '{}' })
      expect(capturedHeaders['Authorization']).toBeUndefined()
    })

    it('protected auth endpoints (auth/me) DO send Authorization header', async () => {
      setToken('valid-token')
      let capturedHeaders: HeadersInit | undefined
      vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
        status: 200,
        headers: { get: () => 'application/json' },
        json: () => Promise.resolve({ ok: true }),
      } as any))
      ;(globalThis.fetch as any).mockImplementation(async (url: string, opts: any) => {
        capturedHeaders = opts.headers
        return {
          status: 200,
          headers: { get: () => 'application/json' },
          json: () => Promise.resolve({ ok: true }),
        } as any
      })

      await api('/auth/me')
      expect(capturedHeaders['Authorization']).toBe('Bearer valid-token')
    })

   it('non-auth endpoints send Authorization header', async () => {
     setToken('valid-token')
     let capturedHeaders: HeadersInit | undefined
     vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
       status: 200,
       headers: { get: () => 'application/json' },
       json: () => Promise.resolve({ ok: true }),
     } as any))
     ;(globalThis.fetch as any).mockImplementation(async (url: string, opts: any) => {
       capturedHeaders = opts.headers
       return {
         status: 200,
         headers: { get: () => 'application/json' },
         json: () => Promise.resolve({ ok: true }),
       } as any
     })

     await api('/dashboard/progress')
     expect(capturedHeaders['Authorization']).toBe('Bearer valid-token')
   })

   it('auth endpoint 401 returns real error, not "Sesión expirada"', async () => {
     setToken('stale-token')
     setTokens('stale-token', 'expired-refresh')
     vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
       status: 401,
       headers: { get: () => 'application/json' },
       json: () => Promise.resolve({ detail: 'Credenciales inválidas' }),
     } as any))

     await expect(api('/auth/login', { method: 'POST', body: '{}' })).rejects.toThrow('Credenciales inválidas')
   })
 })
