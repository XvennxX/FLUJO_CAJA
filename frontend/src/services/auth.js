import api from './api'

// Servicio de autenticación
export const login = async (email, password) => {
  const response = await api.post('/auth/login', {
    username: email, // FastAPI OAuth2 usa 'username' para el email
    password,
  }, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    // Convertir a formato form data
    transformRequest: [(data) => {
      const params = new URLSearchParams()
      params.append('username', data.username)
      params.append('password', data.password)
      return params
    }]
  })
  return response.data
}

export const logout = async () => {
  const response = await api.post('/auth/logout')
  return response.data
}

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me')
  return response.data
}

export const changePassword = async (currentPassword, newPassword, confirmPassword) => {
  const response = await api.post('/auth/change-password', {
    password_actual: currentPassword,
    password_nueva: newPassword,
    confirmar_password: confirmPassword,
  })
  return response.data
}

export const refreshToken = async () => {
  const response = await api.post('/auth/refresh')
  return response.data
}
