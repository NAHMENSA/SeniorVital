import React from 'react'

interface Props {
  message?: string
}

/**
 * LoadingScreen — Optimizado para adultos mayores.
 * - Spinner más grande
 * - Texto más grande
 */
export default function LoadingScreen({ message = 'Cargando...' }: Props) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background" role="status" aria-label={message}>
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-6" />
        <p className="text-xl text-on-surface-variant">{message}</p>
      </div>
    </div>
  )
}
