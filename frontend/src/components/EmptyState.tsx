import React from 'react'

interface Props {
  icon?: string
  title: string
  description?: string
  action?: React.ReactNode
}

/**
 * EmptyState — Optimizado para adultos mayores.
 * - Icono más grande
 * - Texto más grande
 */
export default function EmptyState({ icon = '📭', title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center">
      <span className="text-7xl mb-6" aria-hidden="true">{icon}</span>
      <h3 className="text-xl font-bold text-primary mb-3">{title}</h3>
      {description && <p className="text-lg text-on-surface-variant mb-6 max-w-md">{description}</p>}
      {action}
    </div>
  )
}
