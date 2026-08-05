import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../../store/useAuth'
import { getProgress } from '../../services/dashboard'
import { TrafficLight, AccessibleButton } from '../../components/ui'
import type { ProgressData } from '../../types/models'

/**
 * ProgressPage — Optimizado para adultos mayores.
 * - Tarjetas más grandes, texto y números aumentados
 * - Touch targets 56px mínimo
 */
export default function ProgressPage() {
  const { user } = useAuth()
  const [data, setData] = useState<ProgressData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!user?.id) return
    setLoading(true); setError('')
    try {
      const d = await getProgress(user.id)
      console.debug('[ProgressPage] getProgress', user.id, d)
      setData(d)
    } catch (err) {
      console.error('[ProgressPage] error cargando progreso:', err)
      setError(err instanceof Error ? err.message : 'Error al cargar progreso')
    } finally { setLoading(false) }
  }, [user])

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
        <div className="text-center">
          <p className="text-7xl mb-6" aria-hidden="true">😕</p>
          <p className="text-error font-bold text-xl mb-6" role="alert">{error}</p>
          <AccessibleButton variant="primary" size="lg" onClick={load}>Reintentar</AccessibleButton>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-5">
      <div className="max-w-lg mx-auto flex flex-col gap-8">
        <h1 className="text-2xl text-primary font-bold">Mi progreso</h1>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-5">
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6 text-center">
            <p className="text-4xl font-bold text-secondary">{data?.sessions_this_week || 0}</p>
            <p className="text-base text-on-surface-variant mt-2">Sesiones esta semana</p>
          </div>
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-secondary p-6 text-center">
            <p className="text-4xl font-bold text-primary">{data?.current_streak || 0}</p>
            <p className="text-base text-on-surface-variant mt-2">Días seguidos</p>
          </div>
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-tertiary-fixed p-6 text-center">
            <p className="text-4xl font-bold text-tertiary">{data?.total_sessions || 0}</p>
            <p className="text-base text-on-surface-variant mt-2">Total de sesiones</p>
          </div>
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6 text-center flex items-center justify-center">
            <TrafficLight risk="green" />
          </div>
        </div>

        {/* RPE trend */}
        {data?.rpe_trend && data.rpe_trend.length > 0 && (
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6">
            <h2 className="text-xl font-bold text-primary mb-4">Tendencia de esfuerzo (RPE)</h2>
            <div className="space-y-3">
              {data.rpe_trend.map((point, idx) => (
                <div key={idx} className="flex items-center gap-4">
                  <span className="text-base text-on-surface-variant min-w-[6rem]">{point.date}</span>
                  <div className="flex-1 h-8 bg-surface-container-high rounded-full overflow-hidden">
                    <div className="h-full bg-secondary rounded-full transition-all" style={{ width: `${(point.avg_rpe / 10) * 100}%` }} />
                  </div>
                  <span className="text-base font-bold text-primary min-w-[3rem] text-right">{point.avg_rpe.toFixed(1)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Calendar heatmap */}
        {data?.calendar && Object.keys(data.calendar).length > 0 && (
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6">
            <h2 className="text-xl font-bold text-primary mb-4">Calendario de actividad</h2>
            <div className="grid grid-cols-7 gap-2">
              {['D', 'L', 'M', 'M', 'J', 'V', 'S'].map(d => (
                <span key={d} className="text-base text-center text-on-surface-variant font-bold">{d}</span>
              ))}
              {Object.entries(data.calendar).map(([dateStr, info]) => {
                const d = new Date(dateStr)
                const dayOfWeek = d.getDay()
                const isFirstDay = dateStr === Object.keys(data.calendar!)[0]
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

        {/* AI Insight */}
        {data?.insight && (
          <div className="bg-tertiary-fixed bg-opacity-20 rounded-2xl border-2 border-tertiary-fixed-dim p-6">
            <h2 className="text-xl font-bold text-tertiary mb-3">🧠 Insight del agente</h2>
            <p className="text-lg text-on-surface-variant">{data.insight.message}</p>
          </div>
        )}

        {/* Projection */}
        {data?.projection && (
          <div className="bg-secondary bg-opacity-10 rounded-2xl border-2 border-secondary p-6">
            <h2 className="text-xl font-bold text-primary mb-3">📈 Proyección</h2>
            <p className="text-lg text-on-surface-variant">{data.projection}</p>
          </div>
        )}
      </div>
    </div>
  )
}
