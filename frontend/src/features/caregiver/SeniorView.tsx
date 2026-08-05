import React, { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../../store/useAuth'
import { getSeniorProgress } from '../../services/caregiver'
import { AccessibleButton } from '../../components/ui'
import type { ProgressData } from '../../types/models'

/**
 * SeniorView — Vista detallada del progreso de un senior vinculado.
 * Muestra estadísticas reales obtenidas del dashboard service.
 *
 * Optimizado para adultos mayores con tamaños aumentados.
 */
export default function SeniorView() {
  const { seniorId } = useParams<{ seniorId: string }>()
  const { user } = useAuth()
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [seniorName, setSeniorName] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!seniorId) return
    setLoading(true); setError('')
    try {
      const data = await getSeniorProgress(seniorId)
      setProgress(data.progress)
      setSeniorName(data.senior_name || `Paciente #${seniorId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar progreso')
    } finally {
      setLoading(false)
    }
  }, [seniorId])

  useEffect(() => { load() }, [load])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center" role="status" aria-label="Cargando progreso">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-6" />
          <p className="text-xl text-on-surface-variant">Cargando progreso...</p>
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
          <AccessibleButton variant="primary" size="lg" onClick={load}>Reintentar</AccessibleButton>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-5">
      <div className="max-w-lg mx-auto">
        <Link to="/caregiver" className="text-primary font-bold text-lg hover:underline mb-6 inline-block">
          ← Volver a pacientes
        </Link>
        <h1 className="text-2xl text-primary font-bold mb-6">Progreso de {seniorName}</h1>

        <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6 mb-6">
          <div className="text-center mb-6">
            <p className="text-7xl mb-4" aria-hidden="true">👴</p>
            <p className="text-xl font-bold text-primary">{seniorName}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-surface-container-high rounded-xl p-4 text-center">
              <p className="text-4xl font-bold text-secondary">{progress?.sessions_this_week || 0}</p>
              <p className="text-base text-on-surface-variant mt-2">Sesiones esta semana</p>
            </div>
            <div className="bg-surface-container-high rounded-xl p-4 text-center">
              <p className="text-4xl font-bold text-primary">{progress?.current_streak || 0}</p>
              <p className="text-base text-on-surface-variant mt-2">Días seguidos</p>
            </div>
            <div className="bg-surface-container-high rounded-xl p-4 text-center">
              <p className="text-4xl font-bold text-tertiary">{progress?.total_sessions || 0}</p>
              <p className="text-base text-on-surface-variant mt-2">Total sesiones</p>
            </div>
            <div className="bg-surface-container-high rounded-xl p-4 text-center">
              <p className="text-4xl font-bold text-primary">
                {progress?.rpe_trend && progress.rpe_trend.length > 0
                  ? progress.rpe_trend[progress.rpe_trend.length - 1].avg_rpe.toFixed(1)
                  : '—'}
              </p>
              <p className="text-base text-on-surface-variant mt-2">Último RPE</p>
            </div>
          </div>

          {progress?.rpe_trend && progress.rpe_trend.length > 0 && (
            <div className="mb-6">
              <p className="text-lg font-bold text-primary mb-3">Tendencia de esfuerzo (RPE)</p>
              <div className="space-y-2">
                {progress.rpe_trend.slice(-5).map((point, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <span className="text-base text-on-surface-variant min-w-[5rem]">{point.date}</span>
                    <div className="flex-1 h-6 bg-surface-container-high rounded-full overflow-hidden">
                      <div
                        className="h-full bg-secondary rounded-full transition-all"
                        style={{ width: `${(point.avg_rpe / 10) * 100}%` }}
                      />
                    </div>
                    <span className="text-base font-bold text-primary min-w-[2.5rem] text-right">
                      {point.avg_rpe.toFixed(1)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {progress?.calendar && Object.keys(progress.calendar).length > 0 && (
            <div className="mb-6">
              <p className="text-lg font-bold text-primary mb-3">Calendario de actividad</p>
              <div className="grid grid-cols-7 gap-2">
                {['D', 'L', 'M', 'M', 'J', 'V', 'S'].map(d => (
                  <span key={d} className="text-base text-center text-on-surface-variant font-bold">{d}</span>
                ))}
                {Object.entries(progress.calendar).map(([dateStr, info]) => {
                  const d = new Date(dateStr)
                  const dayOfWeek = d.getDay()
                  const isFirstDay = dateStr === Object.keys(progress.calendar!)[0]
                  return (
                    <React.Fragment key={dateStr}>
                      {isFirstDay && dayOfWeek > 0 && Array.from({ length: dayOfWeek }).map((_, i) => (
                        <div key={`empty-${i}`} />
                      ))}
                      <div
                        className={`aspect-square rounded-lg flex items-center justify-center text-base font-bold ${
                          info.completed ? 'bg-secondary text-on-secondary' : 'bg-surface-container-high text-on-surface-variant'
                        }`}
                        title={`${dateStr}: RPE ${info.rpe_avg?.toFixed(1) || 'N/A'}`}
                      >
                        {d.getDate()}
                      </div>
                    </React.Fragment>
                  )
                })}
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <AccessibleButton variant="primary" size="lg" disabled>
              Enviar mensaje
            </AccessibleButton>
            <AccessibleButton variant="secondary" size="lg" disabled>
              Reporte detallado
            </AccessibleButton>
          </div>
        </div>
      </div>
    </div>
  )
}
