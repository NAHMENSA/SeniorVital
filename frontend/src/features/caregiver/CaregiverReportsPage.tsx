import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../../store/useAuth'
import { getCaregiverReports } from '../../services/caregiver'
import { AccessibleButton } from '../../components/ui'
import type { CaregiverReport } from '../../types/models'

/**
 * CaregiverReportsPage — Página de reportes para cuidadores.
 * Muestra reportes de progreso de los seniors vinculados al cuidador.
 *
 * Optimizado para adultos mayores con tamaños aumentados.
 */
export default function CaregiverReportsPage() {
  const { user } = useAuth()
  const [reports, setReports] = useState<CaregiverReport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!user?.id) return
    setLoading(true); setError('')
    try {
      const data = await getCaregiverReports()
      setReports(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar reportes')
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => { load() }, [load])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center" role="status" aria-label="Cargando reportes">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-6" />
          <p className="text-xl text-on-surface-variant">Cargando reportes...</p>
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
      <div className="max-w-lg mx-auto flex flex-col gap-6">
        <h1 className="text-2xl text-primary font-bold">Reportes de pacientes</h1>

        {reports.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-8 text-center">
            <p className="text-7xl mb-4" aria-hidden="true">📄</p>
            <p className="text-xl text-primary font-bold mb-3">Sin reportes</p>
            <p className="text-lg text-on-surface-variant">
              No hay reportes disponibles de tus pacientes vinculados.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {reports.map((report) => (
              <div
                key={report.id}
                className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6"
                role="article"
                aria-label={`Reporte de ${report.senior_name}`}
              >
                <div className="flex items-start gap-4 mb-4">
                  <span className="text-4xl flex-shrink-0" aria-hidden="true">👴</span>
                  <div className="flex-1">
                    <p className="text-xl font-bold text-primary">{report.senior_name}</p>
                    <p className="text-lg text-on-surface-variant">
                      {new Date(report.period_start).toLocaleDateString('es-ES', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })} - {new Date(report.period_end).toLocaleDateString('es-ES', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-surface-container-high rounded-xl p-3 text-center">
                    <p className="text-2xl font-bold text-secondary">{report.sessions_completed}</p>
                    <p className="text-sm text-on-surface-variant">Sesiones</p>
                  </div>
                  <div className="bg-surface-container-high rounded-xl p-3 text-center">
                    <p className="text-2xl font-bold text-primary">{report.avg_rpe.toFixed(1)}</p>
                    <p className="text-sm text-on-surface-variant">RPE prom.</p>
                  </div>
                  <div className="bg-surface-container-high rounded-xl p-3 text-center">
                    <p className="text-2xl font-bold text-tertiary">{report.streak_days}</p>
                    <p className="text-sm text-on-surface-variant">Racha</p>
                  </div>
                </div>

                {report.recommendations && report.recommendations.length > 0 && (
                  <div className="bg-tertiary-fixed bg-opacity-20 rounded-xl p-4">
                    <p className="text-lg font-bold text-tertiary mb-2">💡 Recomendaciones</p>
                    <ul className="list-disc list-inside space-y-1">
                      {report.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-base text-on-surface-variant">{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
