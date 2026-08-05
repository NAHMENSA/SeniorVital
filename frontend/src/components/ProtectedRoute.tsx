import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../store/useAuth'
import LoadingScreen from './LoadingScreen'
import { SeniorLayout, CaregiverLayout, AdminLayout } from './layouts'

interface Props {
  children: React.ReactNode
  requiredRole?: 'senior' | 'caregiver' | 'admin'
  useLayout?: boolean
}

export default function ProtectedRoute({ children, requiredRole, useLayout = true }: Props) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!user) return <Navigate to="/login" replace />
  if (requiredRole && user.role !== requiredRole) {
    if (user.role === 'senior') return <Navigate to="/routine" replace />
    if (user.role === 'caregiver') return <Navigate to="/caregiver" replace />
    if (user.role === 'admin') return <Navigate to="/admin" replace />
    return <Navigate to="/" replace />
  }
  if (!useLayout) return <>{children}</>
  if (user.role === 'senior') return <SeniorLayout>{children}</SeniorLayout>
  if (user.role === 'caregiver') return <CaregiverLayout>{children}</CaregiverLayout>
  if (user.role === 'admin') return <AdminLayout>{children}</AdminLayout>
  return <>{children}</>
}
