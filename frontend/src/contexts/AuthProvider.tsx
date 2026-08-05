import React, { useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import { clearToken } from '../services/api'

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const init = useAuthStore((s) => s.init)

  useEffect(() => {
    init()
  }, [init])

  useEffect(() => {
    const handler = () => {
      clearToken()
      // Establecer isLoggedOut para evitar que init() intente verificar el token
      useAuthStore.setState({ user: null, isLoggedOut: true })
    }
    window.addEventListener('sv:unauthorized', handler)
    return () => window.removeEventListener('sv:unauthorized', handler)
  }, [])

  return <>{children}</>
}
