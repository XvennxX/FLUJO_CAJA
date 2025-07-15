import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAuthStore = create(
  persist(
    (set, get) => ({
      // Estado inicial
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      // Acciones
      login: (userData, token) => {
        set({
          user: userData,
          token,
          isAuthenticated: true,
          isLoading: false,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        })
        // Limpiar localStorage
        localStorage.removeItem('auth-storage')
      },

      updateUser: (userData) => {
        set((state) => ({
          user: { ...state.user, ...userData },
        }))
      },

      setLoading: (loading) => {
        set({ isLoading: loading })
      },

      // Verificar si el usuario tiene un rol específico
      hasRole: (role) => {
        const { user } = get()
        return user?.rol === role
      },

      // Verificar permisos
      canEdit: () => {
        const { user } = get()
        return ['tesoreria', 'pagaduria'].includes(user?.rol)
      },

      canViewAll: () => {
        const { user } = get()
        return user?.rol === 'tesoreria'
      },

      canEditUsers: () => {
        const { user } = get()
        return user?.rol === 'tesoreria'
      },

      // Obtener token para requests
      getAuthHeader: () => {
        const { token } = get()
        return token ? { Authorization: `Bearer ${token}` } : {}
      },
    }),
    {
      name: 'auth-storage', // nombre en localStorage
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

export { useAuthStore }
