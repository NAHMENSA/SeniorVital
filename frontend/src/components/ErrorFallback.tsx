import React from 'react'
import { AccessibleButton } from './ui/index'

interface Props {
  error?: string
  onRetry?: () => void
}

export default function ErrorFallback({ error = 'Ocurrió un error inesperado', onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background p-4" role="alert">
      <span className="text-5xl mb-4" aria-hidden="true">😕</span>
      <h2 className="text-xl font-bold text-error mb-2">Algo salió mal</h2>
      <p className="text-sm text-on-surface-variant mb-6 text-center max-w-sm">{error}</p>
      {onRetry && (
        <AccessibleButton variant="primary" onClick={onRetry} vibrateOnClick>
          Reintentar
        </AccessibleButton>
      )}
    </div>
  )
}
