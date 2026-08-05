import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../../store/useAuth'
import { getCaregiverAlerts } from '../../services/caregiver'
import { AccessibleButton } from '../../components/ui'
import type { CaregiverAlert } from '../../types/models'

/**
 * CaregiverAlertsPage — Página de alertas para cuidadores.
 * Muestra alertas de fatiga alta, inactividad y otros eventos
 * de los seniors vinculados al cuidador.
 *
 * Optimizado para adultos mayores con tamaños aumentados.
 */
export default function CaregiverAlertsPage() {
  const { user } = useAuth()
  const [alerts, setAlerts] = useState<CaregiverAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!user?.id) return
    setLoading(true); setError('')
    try {
      const data = await getCaregiverAlerts()
      setAlerts(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar alertas')
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => { load() }, [load])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center" role="status" aria-label="Cargando alertas">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-6" />
          <p className="text-xl text-on-surface-variant">Cargando alertas...</p>
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
        <h1 className="text-2xl text-primary font-bold">Alertas de pacientes</h1>

        {alerts.length === 0 ? (
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-8 text-center">
            <p className="text-7xl mb-4" aria-hidden="true">🔔</p>
            <p className="text-xl text-primary font-bold mb-3">Sin alertas</p>
            <p className="text-lg text-on-surface-variant">
              No hay alertas pendientes de tus pacientes vinculados.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`bg-surface-container-lowest rounded-2xl border-2 p-6 ${
                  alert.severity === 'high'
                    ? 'border-error'
                    : alert.severity === 'medium'
                      ? 'border-yellow-500'
                      : 'border-primary'
                }`}
                role="article"
                aria-label={`Alerta: ${alert.title}`}
              >
                <div className="flex items-start gap-4">
                  <span className="text-4xl flex-shrink-0" aria-hidden="true">
                    {alert.type === 'fatigue' ? '😰' : alert.type === 'inactivity' ? '⏰' : '📢'}
                  </span>
                  <div className="flex-1">
                    <p className="text-xl font-bold text-primary mb-2">{alert.title}</p>
                    <p className="text-lg text-on-surface-variant mb-3">{alert.message}</p>
                    <div className="flex items-center gap-3">
                      <span className="text-base text-on-surface-variant">
                        {alert.senior_name}
                      </span>
                      <span className="text-base text-on-surface-variant">•</span>
                      <span className="text-base text-on-surface-variant">
                        {new Date(alert.created_at).toLocaleDateString('es-ES', {
                          day: '2-digit',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
