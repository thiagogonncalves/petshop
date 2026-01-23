import api from './api'

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/users/login/', {
      username,
      password,
    })
    return response.data
  },
  
  async refreshToken(refresh) {
    const response = await api.post('/auth/token/refresh/', {
      refresh,
    })
    return response.data
  },
  
  async getCurrentUser() {
    const response = await api.get('/auth/users/me/')
    return response.data
  },
}
