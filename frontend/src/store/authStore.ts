import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { login as loginApi, register as registerApi, getMe } from '../services/auth'
import { setTokens, clearToken, getToken } from '../services/api'
import type { User, RegisterPayload } from '../types/models'

interface AuthStore {
  user: User | null
  loading: boolean
  isInitialized: boolean
  isLoggedOut: boolean
  login: (email: string, password: string) => Promise<User>
  register: (data: RegisterPayload) => Promise<User>
  logout: () => void
  updateUser: (user: User) => void
  init: () => Promise<void>
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      loading: true,
      isInitialized: false,
      isLoggedOut: false,

      init: async () => {
        const { isLoggedOut } = get()
        
        // Si el usuario hizo logout explícitamente, no intentar verificar token
        if (isLoggedOut) {
          set({ loading: false, isInitialized: true })
          return
        }
        
        const token = getToken()
        if (!token) {
          set({ loading: false, isInitialized: true })
          return
        }
        try {
          const user = await getMe()
          set({ user, loading: false, isInitialized: true })
        } catch {
          clearToken()
          set({ user: null, loading: false, isInitialized: true, isLoggedOut: true })
        }
      },

      login: async (email: string, password: string) => {
        const { access_token, refresh_token } = await loginApi(email, password)
        setTokens(access_token, refresh_token)
        const user = await getMe()
        set({ user, isLoggedOut: false })
        return user
      },

      register: async (data: RegisterPayload) => {
        await registerApi(data)
        const { access_token, refresh_token } = await loginApi(data.email, data.password)
        setTokens(access_token, refresh_token)
        const user = await getMe()
        set({ user, isLoggedOut: false })
        return user
      },

      logout: () => {
        clearToken()
        set({ user: null, isLoggedOut: true })
      },

      updateUser: (user: User) => {
        set({ user })
      },
    }),
    {
      name: 'sv-auth-store',
      partialize: (state) => ({ user: state.user, isLoggedOut: state.isLoggedOut }),
    }
  )
)
