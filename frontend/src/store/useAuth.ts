import { useAuthStore } from './authStore'

export interface AuthState {
  user: ReturnType<typeof useAuthStore>['user']
  loading: ReturnType<typeof useAuthStore>['loading']
  login: ReturnType<typeof useAuthStore>['login']
  register: ReturnType<typeof useAuthStore>['register']
  logout: ReturnType<typeof useAuthStore>['logout']
  updateUser: ReturnType<typeof useAuthStore>['updateUser']
  isSenior: boolean
  isCaregiver: boolean
  isAdmin: boolean
  displayName: string
}

export function useAuth(): AuthState {
  const { user, loading, login, register, logout, updateUser } = useAuthStore()
  return {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    isSenior: user?.role === 'senior',
    isCaregiver: user?.role === 'caregiver',
    isAdmin: user?.role === 'admin',
    displayName: user?.nombre_senior || user?.nombre_cuidador || user?.email || '',
  }
}
