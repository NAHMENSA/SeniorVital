import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import { getTodayRoutine, generateRoutine, generateRoutineStream } from '../../services/routines'
import { AccessibleButton, RpeScale, RestTimer } from '../../components/ui'
import { announce, vibrate } from '../../lib/accessibility'
import { api, addToOfflineQueue } from '../../services/api'
import type { DailyRoutine, RoutineExercise, WorkoutSet } from '../../types/models'

type Phase = 'idle' | 'loading' | 'ready' | 'exercising' | 'resting' | 'rpe' | 'completed'

/**
 * DailyRoutinePage — Optimizado para adultos mayores.
 * - Textos, botones, emojis e iconos aumentados
 * - Touch targets 56px mínimo
 * - Espaciado generoso entre elementos
 */
export default function DailyRoutinePage() {
  const { user, displayName } = useAuth()
  const [phase, setPhase] = useState<Phase>('loading')
  const [routine, setRoutine] = useState<DailyRoutine | null>(null)
  const [currentExerciseIdx, setCurrentExerciseIdx] = useState(0)
  const [currentSet, setCurrentSet] = useState(1)
  const [completedSets, setCompletedSets] = useState<WorkoutSet[]>([])
  const [rpeValue, setRpeValue] = useState<number | null>(null)
  const [error, setError] = useState('')
  const [llmWarning, setLlmWarning] = useState(false)
  const [llmError, setLlmError] = useState<string | null>(null)
  const [llmModel, setLlmModel] = useState<string | null>(null)
  const [generatedBy, setGeneratedBy] = useState<'ollama' | 'fallback'>('fallback')
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [generateStep, setGenerateStep] = useState<string | null>(null)
  const retryCountRef = useRef(0)

  useEffect(() => {
    if (phase !== 'exercising') return
    const interval = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [phase])

  useEffect(() => {
    if (phase !== 'loading') return
    const interval = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [phase])

  useEffect(() => {
    if (phase === 'exercising' || phase === 'loading') {
      setElapsedSeconds(0)
    }
  }, [phase, currentSet])

  const loadRoutine = useCallback(async () => {
    if (!user?.id) return
    setPhase('loading'); setError(''); setLlmWarning(false); setElapsedSeconds(0); setGenerateStep(null); setGeneratedBy('fallback')
    retryCountRef.current = 0

    const applyRoutine = (data: DailyRoutine | null) => {
      if (data && data.llm_available === false) setLlmWarning(true)
      if (data?.llm_model) setLlmModel(data.llm_model)
      if (data?.llm_error) setLlmError(data.llm_error)
      setGeneratedBy(data?.generated_by ?? 'fallback')
      setRoutine(data)
      setGenerateStep(null)
      setPhase(data?.exercises?.length ? 'ready' : 'idle')
    }

    try {
      // 1. Check if a routine already exists for today
      const existing = await getTodayRoutine(user.id)
      if (existing && existing.exercises?.length) {
        applyRoutine(existing)
        return
      }
    } catch {
      // No routine today — proceed to generate
    }

    // 2. Generate via streaming SSE with automatic retry (max 2 retries)
    const attempt = async (): Promise<DailyRoutine | null> => {
      return new Promise((resolve) => {
        generateRoutineStream(
          user.id,
          {
            onProgress: (msg) => setGenerateStep(msg),
            onComplete: (routine) => resolve(routine),
            onError: (err) => {
              const msg = err.message
              const isTimeout = /demasiado tiempo|timeout|Service unavailable|no se pudo conectar|cerró inesperadamente/i.test(msg)
              if (isTimeout && retryCountRef.current < 2) {
                retryCountRef.current += 1
                setGenerateStep(`Reintentando la generación (intento ${retryCountRef.current + 1}/3)...`)
                attempt().then(resolve)
              } else {
                resolve(null)
              }
            },
          },
        )
      })
    }

    const data = await attempt()

    if (data) {
      applyRoutine(data)
      return
    }

    // 3. Fallback: non-streaming endpoint (uses default routine if Ollama fails)
    try {
      const fallback = await generateRoutine(user.id)
      if (fallback && fallback.llm_available === false) {
        setLlmWarning(true)
      }
      applyRoutine(fallback)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al cargar rutina'
      setError(msg)
      setPhase('idle')
    }
  }, [user])

  useEffect(() => { loadRoutine() }, [loadRoutine])

  const currentExercise: RoutineExercise | null = routine?.exercises?.[currentExerciseIdx] || null
  const totalSets = currentExercise?.sets || 3

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleCompleteSet = async () => {
    if (!routine || !currentExercise || !user) return
    vibrate(50)
    announce('Serie completada')

    const setData: WorkoutSet = {
      set_number: currentSet,
      reps: currentExercise.reps_per_set,
      rpe: 0,
      completed_at: new Date().toISOString(),
      rest_duration_sec: currentExercise.rest_duration_sec,
    }

    if (currentSet < totalSets) {
      setCompletedSets(prev => [...prev, setData])
      setPhase('resting')
    } else {
      setCompletedSets(prev => [...prev, setData])
      setPhase('rpe')
    }
  }

  const handleRpeSubmit = async (rpe: number) => {
    if (!routine || !currentExercise || !user) return
    setRpeValue(rpe)
    vibrate(50)

    const payload = {
      user_id: user.id,
      exercise_id: currentExercise.exercise_id,
      sets: currentSet,
      reps: currentExercise.reps_per_set,
      rpe,
      completed_at: new Date().toISOString(),
    }

    try {
      await api('/tracking/record', { method: 'POST', body: JSON.stringify(payload) })
    } catch (err) {
      console.error('[DailyRoutinePage] fallo tracking/record, encolado offline:', payload, err)
      await addToOfflineQueue({ path: '/tracking/record', method: 'POST', body: payload })
    }

    if (currentExerciseIdx < (routine.exercises?.length || 1) - 1) {
      setCurrentExerciseIdx(i => i + 1)
      setCurrentSet(1)
      setRpeValue(null)
      setPhase('ready')
    } else {
      setPhase('completed')
      announce('Rutina completada')
    }
  }

  const handleRestComplete = () => {
    setCurrentSet(s => s + 1)
    setPhase('exercising')
  }

  const handleRestSkip = () => {
    setCurrentSet(s => s + 1)
    setPhase('exercising')
  }

  if (phase === 'loading') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center" role="status" aria-label="Cargando rutina">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-6" />
          <p className="text-xl text-on-surface-variant">Preparando tu rutina...</p>
          {generateStep ? (
            <p className="text-base text-on-surface-variant mt-3">
              {generateStep}
            </p>
          ) : (
            <p className="text-sm text-on-surface-variant mt-2">
              Esto puede tomar hasta 3 minutos (IA generando tu rutina personalizada)
            </p>
          )}
          {llmModel && (
            <p className="text-xs text-on-surface-variant mt-1">
              Modelo LLM Local Ollama: {llmModel}
            </p>
          )}
          <p className="text-2xl font-mono font-bold text-secondary mt-4" aria-label={`Tiempo transcurrido: ${formatTime(elapsedSeconds)}`}>
            {formatTime(elapsedSeconds)}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="text-center max-w-lg">
          <p className="text-7xl mb-6" aria-hidden="true">😕</p>
          <p className="text-error font-bold text-xl mb-6" role="alert">{error}</p>
          <AccessibleButton variant="primary" size="lg" onClick={loadRoutine} vibrateOnClick>
            Reintentar
          </AccessibleButton>
        </div>
      </div>
    )
  }

  if (phase === 'idle' || !routine) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="text-center max-w-lg">
          <p className="text-7xl mb-6" aria-hidden="true">🏋️</p>
          <h1 className="text-2xl text-primary font-bold mb-4">¡Bienvenido, {displayName}!</h1>
          <p className="text-lg text-on-surface-variant mb-8">Hoy no tienes una rutina asignada. ¿Quieres que generemos una?</p>
          <AccessibleButton variant="primary" size="lg" onClick={loadRoutine} vibrateOnClick>
            Generar rutina
          </AccessibleButton>
        </div>
      </div>
    )
  }

  if (phase === 'completed') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="text-center max-w-lg">
          <p className="text-8xl mb-6" aria-hidden="true">🎉</p>
          <h1 className="text-2xl text-primary font-bold mb-4">¡Rutina completada!</h1>
          <p className="text-lg text-on-surface-variant mb-8">Gran trabajo hoy. Sigue así.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/progress">
              <AccessibleButton variant="primary" size="lg" vibrateOnClick>Ver mi progreso</AccessibleButton>
            </Link>
            <Link to="/habits">
              <AccessibleButton variant="secondary" size="lg">Registrar hábitos</AccessibleButton>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-5 flex flex-col">
      <div className="max-w-lg mx-auto w-full flex-1 flex flex-col">
        {/* LLM Warning Alert */}
        {llmWarning && (
          <div
            className="mb-6 p-5 rounded-xl border-2 border-yellow-500 bg-yellow-50 text-yellow-900"
            role="alert"
            aria-live="polite"
          >
            <div className="flex items-start gap-4">
              <span className="text-4xl flex-shrink-0" aria-hidden="true">⚠️</span>
             <div>
                 <p className="font-bold text-lg">Modelo LLM no está corriendo</p>
                 <p className="text-base mt-2">
                   Se cargó una rutina predeterminada. Para rutinas personalizadas con IA, verifica que Ollama esté activo.
                 </p>
                 {llmError && (
                   <p className="text-sm mt-1 text-yellow-800">
                     Error: {llmError}
                   </p>
                 )}
               </div>
            </div>
          </div>
        )}

        {/* Progress header */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-3">
            <span className="text-lg text-on-surface-variant">
              Ejercicio {currentExerciseIdx + 1} de {routine.exercises?.length || 0}
            </span>
            <span className="text-lg font-bold text-primary">
              Serie {currentSet} de {totalSets}
            </span>
          </div>
          <div className="w-full h-4 bg-surface-container-high rounded-full" role="progressbar" aria-valuenow={((currentExerciseIdx * totalSets + currentSet) / ((routine.exercises?.length || 1) * totalSets)) * 100} aria-valuemin={0} aria-valuemax={100}>
            <div className="h-full bg-secondary rounded-full transition-all duration-300" style={{ width: `${((currentExerciseIdx * totalSets + currentSet) / ((routine.exercises?.length || 1) * totalSets)) * 100}%` }} />
          </div>
        </div>

        {currentExercise && phase === 'ready' && (
          <div className="flex-1 flex flex-col items-center justify-center text-center gap-6">
            <div className="w-40 h-40 bg-surface-container-high rounded-2xl flex items-center justify-center">
              <span className="text-7xl">🏃</span>
            </div>
            <h2 className="text-3xl text-primary font-bold">{currentExercise.name}</h2>
            <p className="text-sm text-on-surface-variant" data-testid="routine-origin" aria-label="Origen de la rutina">
              {generatedBy === 'ollama'
                ? 'Rutina generada con IA (Ollama phi3:mini)'
                : 'Rutina predeterminada (IA no disponible)'}
            </p>
            {currentExercise.description && (
              <p className="text-lg text-on-surface-variant">{currentExercise.description}</p>
            )}
            <p className="text-xl">
              <span className="font-bold">{currentExercise.reps_per_set} repeticiones</span>
              {currentExercise.rest_duration_sec > 0 && (
                <span className="text-on-surface-variant ml-3">· {currentExercise.rest_duration_sec}s descanso</span>
              )}
            </p>
            <AccessibleButton variant="primary" size="lg" onClick={() => setPhase('exercising')} vibrateOnClick announceText="Ejercicio iniciado">
              ¡Empezar!
            </AccessibleButton>
          </div>
        )}

        {phase === 'exercising' && (
          <div className="flex-1 flex flex-col items-center justify-center text-center gap-8">
            <p className="text-7xl">💪</p>
            <h2 className="text-2xl text-primary font-bold">Realizando ejercicio</h2>
            <p className="text-xl text-on-surface-variant">
              Serie {currentSet} de {totalSets}
            </p>
            <p className="text-6xl font-mono font-bold text-secondary" aria-live="off" aria-label={`Tiempo transcurrido: ${formatTime(elapsedSeconds)}`}>
              {formatTime(elapsedSeconds)}
            </p>
            <AccessibleButton variant="primary" size="lg" onClick={handleCompleteSet} vibrateOnClick announceText="Serie completada">
              Serie completada
            </AccessibleButton>
          </div>
        )}

        {phase === 'resting' && (
          <div className="flex-1 flex items-center justify-center">
            <RestTimer
              key={`rest-${currentExerciseIdx}-${currentSet}`}
              durationSec={currentExercise?.rest_duration_sec || 30}
              onComplete={handleRestComplete}
              onSkip={handleRestSkip}
            />
          </div>
        )}

        {phase === 'rpe' && (
          <div className="flex-1 flex flex-col items-center justify-center gap-6">
            <RpeScale value={rpeValue} onChange={handleRpeSubmit} />
            {currentSet < totalSets && (
              <AccessibleButton variant="ghost" size="lg" onClick={() => { setPhase('resting') }}>
                Descansar antes de continuar
              </AccessibleButton>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
