import React, { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import { getLinkedSeniors, linkSenior } from '../../services/caregiver'
import { AccessibleButton } from '../../components/ui'
import type { CaregiverLink } from '../../types/models'

export default function CaregiverDashboard() {
  const { user } = useAuth()
  const [seniors, setSeniors] = useState<CaregiverLink[]>([])
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const data = await getLinkedSeniors()
      setSeniors(data)
    } catch { /* no seniors yet */ }
  }, [])

  useEffect(() => { load() }, [load])

  const handleLink = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return
    setBusy(true); setError('')
    try {
      await linkSenior(email.trim())
      setEmail('')
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al vincular')
    } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto flex flex-col gap-6">
        <h1 className="text-xl text-primary font-bold">Mis pacientes</h1>

        {/* Link form */}
        <form onSubmit={handleLink} className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-4">
          <p className="font-bold text-primary mb-3">Vincular nuevo paciente</p>
          {error && <div className="bg-error-container text-on-error-container p-3 rounded-lg text-sm font-semibold mb-3" role="alert">{error}</div>}
          <div className="flex gap-2">
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="Email del senior"
              className="flex-1 h-12 px-4 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-base"
              required />
            <AccessibleButton type="submit" variant="primary" disabled={busy}>
              {busy ? '...' : 'Vincular'}
            </AccessibleButton>
          </div>
        </form>

        {/* Senior list */}
        {seniors.length === 0 ? (
          <div className="text-center p-8">
            <p className="text-5xl mb-4" aria-hidden="true">👨‍👩‍👧‍👦</p>
            <p className="text-on-surface-variant">No tienes pacientes vinculados aún.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {seniors.map(s => (
              <Link key={s.id} to={`/caregiver/senior/${s.senior_user_id}`}
                className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-4 flex items-center gap-4 hover:brightness-110 transition-all focus:outline-none focus:ring-4 focus:ring-primary"
              >
                <span className="text-3xl" aria-hidden="true">👴</span>
                <div>
                  <p className="font-bold text-primary">{s.senior_name || 'Senior'}</p>
                  <p className="text-sm text-on-surface-variant">Ver progreso →</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
