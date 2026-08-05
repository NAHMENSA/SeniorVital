import React from 'react'
import { useAuth } from '../../store/useAuth'
import { AccessibleButton } from '../../components/ui'
import { EmptyState } from '../../components'

export default function ProfilePage() {
  const { user, logout } = useAuth()

  if (!user) return <EmptyState icon="👤" title="No has iniciado sesión" />

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto flex flex-col gap-6">
        <h1 className="text-xl text-primary font-bold">Mi perfil</h1>

        <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center text-2xl text-on-secondary font-bold">
              {(user.nombre_senior || user.nombre_cuidador || user.email || '?')[0].toUpperCase()}
            </div>
            <div>
              <p className="text-lg font-bold text-primary">{user.nombre_senior || user.nombre_cuidador || 'Usuario'}</p>
              <p className="text-sm text-on-surface-variant">{user.email}</p>
              <span className="inline-block mt-1 px-2 py-0.5 bg-secondary bg-opacity-20 text-secondary text-xs font-bold rounded-full">
                {user.role === 'senior' ? 'Adulto mayor' : user.role === 'caregiver' ? 'Cuidador' : 'Administrador'}
              </span>
            </div>
          </div>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between py-2 border-b border-outline-variant">
              <span className="text-on-surface-variant">Miembro desde</span>
              <span className="font-semibold">{user.created_at ? new Date(user.created_at).toLocaleDateString('es-ES') : '—'}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-outline-variant">
              <span className="text-on-surface-variant">Estado</span>
              <span className="font-semibold text-green-600">{user.is_active ? 'Activo' : 'Inactivo'}</span>
            </div>
            {user.health_profile && (
              <div className="flex justify-between py-2 border-b border-outline-variant">
                <span className="text-on-surface-variant">Edad</span>
                <span className="font-semibold">{user.health_profile.age || '—'}</span>
              </div>
            )}
          </div>
        </div>

        <AccessibleButton variant="danger" onClick={logout} className="w-full">
          Cerrar sesión
        </AccessibleButton>
      </div>
    </div>
  )
}
