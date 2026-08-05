import { describe, it, expect, vi, beforeEach } from 'vitest'
import { login, register, getMe, updateHealthProfile } from '../auth'

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('auth service', () => {
  it('login calls POST /auth/login', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ access_token: 'abc', refresh_token: 'def', token_type: 'bearer' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const result = await login('test@test.com', 'password123')
    expect(result.access_token).toBe('abc')
    expect(result.refresh_token).toBe('def')
    expect(mockFetch).toHaveBeenCalledWith('/auth/login', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ email: 'test@test.com', password: 'password123' }),
    }))
  })

  it('getMe calls GET /auth/me', async () => {
    const mockUser = { id: '1', email: 'test@test.com', role: 'senior' }
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockUser,
    })
    vi.stubGlobal('fetch', mockFetch)

    const result = await getMe()
    expect(result.id).toBe('1')
    expect(mockFetch).toHaveBeenCalledWith('/auth/me', expect.any(Object))
  })

  it('updateHealthProfile calls PUT /auth/profile', async () => {
    const profile = { age: 70, weight_kg: 75 }
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ detail: 'Profile updated' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    await updateHealthProfile(profile)
    expect(mockFetch).toHaveBeenCalledWith('/auth/profile', expect.objectContaining({
      method: 'PUT',
    }))
  })
})
