import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import { AccessibleButton } from '../../components/ui'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(''); setBusy(true)
    try {
      const user = await login(email.trim(), password)
      if (user.role === 'senior') navigate('/routine')
      else if (user.role === 'caregiver') navigate('/caregiver')
      else if (user.role === 'admin') navigate('/admin')
      else navigate('/')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
    } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-5">
      <form onSubmit={handleSubmit} className="w-full max-w-lg bg-surface-container-lowest rounded-2xl border-2 border-primary p-8 shadow-sm flex flex-col gap-5">
        <h1 className="text-2xl text-primary font-bold text-center">SeniorVital</h1>
        <p className="text-xl text-on-surface-variant text-center">Inicia sesión</p>

        {error && <div className="bg-error-container text-on-error-container p-4 rounded-xl text-base font-semibold" role="alert">{error}</div>}

        <label className="flex flex-col gap-2">
          <span className="text-primary font-bold text-lg">Correo electrónico</span>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)}
            className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-lg"
            autoComplete="email" required />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-primary font-bold text-lg">Contraseña</span>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)}
            className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-lg"
            autoComplete="current-password" required />
        </label>

        <AccessibleButton type="submit" variant="primary" size="lg" disabled={busy} className="w-full mt-3">
          {busy ? 'Entrando...' : 'Entrar'}
        </AccessibleButton>

        <p className="text-center text-lg text-black">
          ¿Ya tienes cuenta?{' '}
          <Link to="/" className="text-black font-bold hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded">Regístrate</Link>
        </p>
      </form>
    </div>
  )
}
