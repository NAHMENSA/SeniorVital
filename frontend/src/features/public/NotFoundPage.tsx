import React from 'react'
import { Link } from 'react-router-dom'
import { AccessibleButton } from '../../components/ui'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <span className="text-7xl block mb-4" aria-hidden="true">🔍</span>
        <h1 className="text-3xl font-bold text-primary mb-2">Página no encontrada</h1>
        <p className="text-lg text-on-surface-variant mb-6">La página que buscas no existe o ha sido movida.</p>
        <Link to="/">
          <AccessibleButton variant="primary" size="lg">Volver al inicio</AccessibleButton>
        </Link>
      </div>
    </div>
  )
}
