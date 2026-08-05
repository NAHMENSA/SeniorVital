import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import { updateHealthProfile } from '../../services/auth'
import { AccessibleButton } from '../../components/ui'
import type { HealthProfile, FitnessLevel, Goal, MedicalRestriction, Equipment } from '../../types/models'

const STEPS = ['Edad y peso', 'Condición física', 'Objetivos', 'Restricciones médicas', 'Equipamiento']

/**
 * HealthProfileOnboarding — Optimizado para adultos mayores.
 * - Inputs grandes (h-16), texto grande
 * - Botones de selección con min-h 56px
 * - Touch targets 56px mínimo
 */
export default function HealthProfileOnboarding() {
  const { user, updateUser } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [profile, setProfile] = useState<Partial<HealthProfile>>({
    age: 65, weight_kg: 70, height_cm: 160, goals: [], medical_restrictions: [], equipment: [],
  })

  const update = (partial: Partial<HealthProfile>) => setProfile(p => ({ ...p, ...partial }))

  const toggleArray = <T,>(arr: T[] | undefined, item: T): T[] => {
    if (!arr) return [item]
    return arr.includes(item) ? arr.filter(i => i !== item) : [...arr, item]
  }

  const handleFinish = async () => {
    setError(''); setBusy(true)
    try {
      if (!profile.age || profile.age < 60) { setError('Debes tener 60 años o más'); setBusy(false); return }
      if (!profile.weight_kg || profile.weight_kg <= 0) { setError('Peso inválido'); setBusy(false); return }
      const updated = await updateHealthProfile(profile as HealthProfile)
      updateUser(updated)
      navigate('/routine')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al guardar perfil')
    } finally { setBusy(false) }
  }

  const renderStep = () => {
    switch (step) {
      case 0: return (
        <div className="flex flex-col gap-5">
          <label className="flex flex-col gap-2">
            <span className="text-primary font-bold text-lg">Edad</span>
            <input type="number" value={profile.age || ''} onChange={e => update({ age: parseInt(e.target.value) || 0 })}
              className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface text-3xl text-center font-bold" min={60} max={120} /></label>
          <label className="flex flex-col gap-2">
            <span className="text-primary font-bold text-lg">Peso (kg)</span>
            <input type="number" value={profile.weight_kg || ''} onChange={e => update({ weight_kg: parseFloat(e.target.value) || 0 })}
              className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface text-3xl text-center font-bold" min={30} max={250} step={0.1} /></label>
          <label className="flex flex-col gap-2">
            <span className="text-primary font-bold text-lg">Altura (cm)</span>
            <input type="number" value={profile.height_cm || ''} onChange={e => update({ height_cm: parseInt(e.target.value) || 0 })}
              className="w-full h-16 px-5 rounded-xl border-2 border-outline-variant bg-surface text-3xl text-center font-bold" min={100} max={250} /></label>
        </div>
      )
      case 1: return (
        <div className="flex flex-col gap-4">
          <p className="text-primary font-bold text-lg mb-3">¿Cómo describirías tu condición física actual?</p>
          {(['principiante', 'intermedio', 'avanzado'] as FitnessLevel[]).map(l => (
            <button key={l} onClick={() => update({ fitness_level: l })}
              className={`w-full min-h-[4rem] rounded-xl border-2 font-bold text-lg transition-all ${
                profile.fitness_level === l ? 'bg-secondary text-on-secondary border-secondary' : 'bg-surface text-primary border-outline-variant hover:bg-surface-container-high'
              }`}>
              {l === 'principiante' ? 'Principiante (poco activo)' : l === 'intermedio' ? 'Intermedio (activo)' : 'Avanzado (muy activo)'}
            </button>
          ))}
        </div>
      )
      case 2: return (
        <div className="flex flex-col gap-4">
          <p className="text-primary font-bold text-lg mb-3">¿Cuáles son tus objetivos? (puedes elegir varios)</p>
          {(['movilidad', 'fuerza', 'flexibilidad', 'equilibrio', 'resistencia'] as Goal[]).map(g => (
            <button key={g} onClick={() => update({ goals: toggleArray(profile.goals, g) })}
              className={`w-full min-h-[4rem] rounded-xl border-2 font-bold text-lg transition-all ${
                profile.goals?.includes(g) ? 'bg-secondary text-on-secondary border-secondary' : 'bg-surface text-primary border-outline-variant hover:bg-surface-container-high'
              }`}>
              {g === 'movilidad' ? '🦵 Mejorar movilidad' : g === 'fuerza' ? '💪 Ganar fuerza' : g === 'flexibilidad' ? '🤸 Más flexibilidad' : g === 'equilibrio' ? '🧘 Mejorar equilibrio' : '❤️ Más resistencia'}
            </button>
          ))}
        </div>
      )
      case 3: return (
        <div className="flex flex-col gap-4">
          <p className="text-primary font-bold text-lg mb-3">¿Tienes alguna de estas condiciones? (selecciona todas las que apliquen)</p>
          {([
            ['artrosis_rodilla', 'Artrosis de rodilla'],
            ['osteoporosis', 'Osteoporosis'],
            ['hipertension', 'Hipertensión'],
            ['artritis', 'Artritis'],
            ['dolor_articular', 'Dolor articular crónico'],
            ['prótesis', 'Prótesis de cadera'],
            ['diabetes', 'Diabetes'],
            ['cardiopatia', 'Cardiopatía'],
          ] as [MedicalRestriction, string][]).map(([key, label]) => (
            <button key={key} onClick={() => update({ medical_restrictions: toggleArray(profile.medical_restrictions, key) })}
              className={`w-full min-h-[4rem] rounded-xl border-2 font-semibold text-lg text-left px-5 transition-all ${
                profile.medical_restrictions?.includes(key) ? 'bg-secondary text-on-secondary border-secondary' : 'bg-surface text-primary border-outline-variant hover:bg-surface-container-high'
              }`}>
              {label}
            </button>
          ))}
        </div>
      )
      case 4: return (
        <div className="flex flex-col gap-4">
          <p className="text-primary font-bold text-lg mb-3">¿Qué equipamiento tienes disponible?</p>
          {([
            ['ninguno', 'Ninguno, solo mi cuerpo'],
            ['silla', 'Una silla resistente'],
            ['bandas_elasticas', 'Bandas elásticas'],
            ['pesas_ligeras', 'Pesas ligeras (1-3 kg)'],
            ['colchoneta', 'Colchoneta / tapete'],
          ] as [Equipment, string][]).map(([key, label]) => (
            <button key={key} onClick={() => update({ equipment: toggleArray(profile.equipment, key) })}
              className={`w-full min-h-[4rem] rounded-xl border-2 font-semibold text-lg text-left px-5 transition-all ${
                profile.equipment?.includes(key) ? 'bg-secondary text-on-secondary border-secondary' : 'bg-surface text-primary border-outline-variant hover:bg-surface-container-high'
              }`}>
              {label}
            </button>
          ))}
        </div>
      )
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-5">
      <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl border-2 border-primary p-8 shadow-sm">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-xl text-primary font-bold">Tu perfil de salud</h1>
          <span className="text-lg text-on-surface-variant font-semibold">Paso {step + 1} de 5</span>
        </div>

        <div className="w-full h-4 bg-surface-container-high rounded-full mb-8" role="progressbar" aria-valuenow={((step + 1) / 5) * 100} aria-valuemin={0} aria-valuemax={100}>
          <div className="h-full bg-secondary rounded-full transition-all duration-300" style={{ width: `${((step + 1) / 5) * 100}%` }} />
        </div>

        <p className="text-lg text-primary font-bold mb-6">{STEPS[step]}</p>

        {error && <div className="bg-error-container text-on-error-container p-4 rounded-xl text-base font-semibold mb-6" role="alert">{error}</div>}

        {renderStep()}

        <div className="flex justify-between mt-8 gap-4">
          {step > 0 ? (
            <AccessibleButton variant="ghost" onClick={() => setStep(s => s - 1)} size="lg">Anterior</AccessibleButton>
          ) : <div />}
          {step < 4 ? (
            <AccessibleButton variant="primary" onClick={() => setStep(s => s + 1)} size="lg">Siguiente</AccessibleButton>
          ) : (
            <AccessibleButton variant="primary" size="lg" disabled={busy} onClick={handleFinish} vibrateOnClick announceText="Perfil guardado">
              {busy ? 'Guardando...' : '¡Listo!'}
            </AccessibleButton>
          )}
        </div>
      </div>
    </div>
  )
}
