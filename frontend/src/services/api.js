import axios from 'axios'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

// Configuración base de axios
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para añadir token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { logout } = useAuthStore.getState()
    
    if (error.response?.status === 401) {
      // Token expirado o inválido
      logout()
      toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      toast.error('No tienes permisos para realizar esta acción')
    } else if (error.response?.status >= 500) {
      toast.error('Error del servidor. Intenta nuevamente.')
    }
    
    return Promise.reject(error)
  }
)

export default api
export { API_BASE_URL }
