import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from '../LoginPage'

vi.mock('../../../store/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn(),
    user: null,
    loading: false,
  }),
}))

describe('LoginPage', () => {
  it('renders login form', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )
    expect(screen.getByText('SeniorVital')).toBeDefined()
    expect(screen.getByText('Inicia sesión')).toBeDefined()
    expect(screen.getByText('Entrar')).toBeDefined()
  })

  it('has email and password fields', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    )
    expect(screen.getByLabelText('Correo electrónico')).toBeDefined()
    expect(screen.getByLabelText('Contraseña')).toBeDefined()
  })
})
