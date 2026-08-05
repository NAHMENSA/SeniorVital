import { api } from './api'
import type { AuthResponse, User, RegisterPayload } from '../types/models'

export function register(data: RegisterPayload) {
  return api<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function login(email: string, password: string) {
  return api<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function getMe() {
  return api<User>('/auth/me')
}

export function updateHealthProfile(profile: Record<string, unknown>) {
  return api<User>('/auth/profile', {
    method: 'PUT',
    body: JSON.stringify({ profile, health_profile: profile }),
  })
}
