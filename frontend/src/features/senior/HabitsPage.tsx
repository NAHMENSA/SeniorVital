import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../../store/useAuth'
import { getTodayHabits, saveHabits } from '../../services/habits'
import { AccessibleButton } from '../../components/ui'
import { announce } from '../../lib/accessibility'
import { addToOfflineQueue } from '../../services/api'
import type { DailyHabits } from '../../types/models'

/**
 * HabitsPage — Optimizado para adultos mayores.
 * - Contadores y botones más grandes
 * - Touch targets 56px mínimo
 */
export default function HabitsPage() {
  const { user } = useAuth()
  const [water, setWater] = useState(4)
  const [sleep, setSleep] = useState(7)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const loadHabits = useCallback(async () => {
    if (!user?.id) return
    try {
      const data = await getTodayHabits(user.id)
        if (data) {
          setWater(data.water_intake_glasses ?? 0)
          setSleep(data.sleep_hours ?? 0)
        }
    } catch { /* defaults */ }
  }, [user])

  useEffect(() => { loadHabits() }, [loadHabits])

  const handleSave = async () => {
    if (!user?.id) return
    setBusy(true); setError('')
    const data = {
      user_id: user.id,
      date: new Date().toISOString().split('T')[0],
      water_intake_glasses: water,
      sleep_hours: sleep,
    }
    try {
      await saveHabits(data)
      announce('Hábitos guardados')
      await addToOfflineQueue({ path: '/habits', method: 'POST', body: data })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar')
    } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen bg-background p-5">
      <div className="max-w-lg mx-auto flex flex-col gap-8">
        <h1 className="text-2xl text-primary font-bold">Hábitos diarios</h1>

        {error && <div className="bg-error-container text-on-error-container p-4 rounded-xl text-lg font-semibold" role="alert">{error}</div>}

        {/* Water */}
        <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-8">
          <p className="text-xl font-bold text-primary mb-6">💧 Vasos de agua</p>
          <div className="flex items-center justify-center gap-6">
            <AccessibleButton variant="secondary" size="lg" onClick={() => setWater(w => Math.max(0, (w || 0) - 1))} aria-label="Quitar un vaso">−</AccessibleButton>
            <span className="text-7xl font-bold text-secondary min-w-[7rem] text-center">{water ?? 0}</span>
            <AccessibleButton variant="secondary" size="lg" onClick={() => setWater(w => (w || 0) + 1)} aria-label="Agregar un vaso">+</AccessibleButton>
          </div>
          <p className="text-center text-lg text-on-surface-variant mt-4">Recomendado: 6-8 vasos</p>
        </div>

        {/* Sleep */}
        <div className="bg-surface-container-lowest rounded-2xl border-2 border-secondary p-8">
          <p className="text-xl font-bold text-primary mb-6">🌙 Horas de sueño</p>
          <div className="flex items-center justify-center gap-6">
            <AccessibleButton variant="secondary" size="lg" onClick={() => setSleep(s => Math.max(0, +((s || 0) - 0.5).toFixed(1)))} aria-label="Restar media hora">−</AccessibleButton>
            <span className="text-7xl font-bold text-secondary min-w-[7rem] text-center">{sleep ?? 0}</span>
            <AccessibleButton variant="secondary" size="lg" onClick={() => setSleep(s => Math.min(12, +((s || 0) + 0.5).toFixed(1)))} aria-label="Agregar media hora">+</AccessibleButton>
          </div>
          <p className="text-center text-lg text-on-surface-variant mt-4">Recomendado: 7-9 horas</p>
        </div>

        <AccessibleButton variant="primary" size="lg" disabled={busy} onClick={handleSave} className="w-full">
          {busy ? 'Guardando...' : 'Guardar hábitos'}
        </AccessibleButton>
      </div>
    </div>
  )
}
