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

  async firstLoginChangePassword(newUsername, newPassword, newPasswordConfirm) {
    const response = await api.post('/auth/first-login/', {
      new_username: newUsername,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    })
    return response.data
  },
}
