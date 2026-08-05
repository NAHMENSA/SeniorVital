import React, { memo } from 'react'
import type { RiskTrafficLight } from '../../types/models'

const config: Record<RiskTrafficLight, { color: string; label: string }> = {
  green: { color: 'bg-green-500', label: 'Ritmo estable' },
  amber: { color: 'bg-yellow-500', label: 'Riesgo de abandono' },
  red: { color: 'bg-red-500', label: 'Inactivo o fatiga severa' },
}

/**
 * TrafficLight — Optimizado para adultos mayores.
 * - Indicador de color más grande
 * - Texto más grande
 */
const TrafficLight = memo(function TrafficLight({ risk }: { risk: RiskTrafficLight }) {
  const c = config[risk]
  return (
    <div className="flex items-center gap-3" role="status" aria-label={c.label}>
      <span className={`w-6 h-6 rounded-full ${c.color} shadow-sm`} />
      <span className="text-lg font-semibold text-on-surface-variant">{c.label}</span>
    </div>
  )
})

export default TrafficLight
