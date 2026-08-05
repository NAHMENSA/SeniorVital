import React, { useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import { AccessibleButton } from '../../components/ui'
import type { Role } from '../../types/models'

export default function RegisterPage() {
  const [searchParams] = useSearchParams()
  const roleParam = (searchParams.get('role') || 'senior') as Role
  const { register } = useAuth()
  const navigate = useNavigate()

  const [role] = useState<Role>(roleParam)
  const [nombreSenior, setNombreSenior] = useState('')
  const [nombreCuidador, setNombreCuidador] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const isSenior = role === 'senior'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (isSenior && !nombreSenior.trim()) { setError('El nombre es obligatorio'); return }
    if (!isSenior && !nombreCuidador.trim()) { setError('El nombre es obligatorio'); return }
    setBusy(true)
    try {
      await register({
        email: email.trim(),
        password,
        role,
        nombre_senior: isSenior ? nombreSenior.trim() : undefined,
        nombre_cuidador: !isSenior ? nombreCuidador.trim() : undefined,
      })
      if (isSenior) navigate('/onboarding/health-profile')
      else navigate('/caregiver')
     } catch (err: unknown) {
      console.error('Error en registro:', err)
      if (err instanceof Error) {
        const msg = err.message.includes('ya registrado')
          ? 'Este correo ya está registrado. Inicia sesión o usa otro correo.'
          : err.message.includes('Error interno')
          ? 'No pudimos crear tu cuenta. Inténtalo más tarde.'
          : err.message
        setError(msg)
      } else {
        setError('No pudimos crear tu cuenta. Verifica los datos e intenta nuevamente.')
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-5">
      <form onSubmit={handleSubmit} className="w-full max-w-lg bg-surface-container-lowest rounded-2xl border-2 border-primary p-8 shadow-sm flex flex-col gap-5">
        <h1 className="text-2xl text-primary font-bold text-center">
          {isSenior ? 'Registro Senior' : 'Registro Cuidador'}
        </h1>

        {error && <div className="bg-error-container text-on-error-container p-4 rounded-xl text-base font-semibold" role="alert">{error}</div>}

        <label className="flex flex-col gap-2">
          <span className="text-primary font-bold text-lg">
            {isSenior ? 'Nombre completo' : 'Nombre completo del cuidador'}
          </span>
          <input
            type="text"
            value={isSenior ? nombreSenior : nombreCuidador}
            onChange={e => isSenior ? setNombreSenior(e.target.value) : setNombreCuidador(e.target.value)}
            className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-lg"
            placeholder={isSenior ? 'Ej: Juan Pérez' : 'Ej: María García'}
            autoComplete="name"
            required
            aria-required="true"
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-primary font-bold text-lg">Correo electrónico</span>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)}
            className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-lg"
            placeholder="ejemplo@correo.com" autoComplete="email" required />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-primary font-bold text-lg">Contraseña</span>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)}
            className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-lg"
            placeholder="Mínimo 6 caracteres" autoComplete="new-password" required minLength={6} />
        </label>

        <AccessibleButton type="submit" variant="primary" size="lg" disabled={busy} className="w-full mt-3">
          {busy ? 'Registrando...' : 'Crear cuenta'}
        </AccessibleButton>

        <p className="text-center text-lg text-black">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-black font-bold hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded">Inicia sesión</Link>
        </p>
      </form>
    </div>
  )
}
