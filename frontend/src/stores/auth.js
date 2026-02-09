import { defineStore } from 'pinia'
import { authService } from '@/services/auth'
import router from '@/router'

function loadStoredUser() {
  try {
    const s = localStorage.getItem('auth_user')
    return s ? JSON.parse(s) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: loadStoredUser(),
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    userRole: (state) => state.user?.role,
    isAdmin: (state) => {
      const u = state.user
      if (!u) return false
      if (u.is_superuser || u.is_staff) return true
      const r = u.role
      return r === 'admin' || r === 'ADMIN'
    },
    isManager: (state) => {
      const r = state.user?.role
      return r === 'manager' || r === 'admin' || r === 'MANAGER' || r === 'ADMIN'
    },
  },
  
  actions: {
    async login(username, password) {
      try {
        const data = await authService.login(username, password)
        this.token = data.access
        this.refreshToken = data.refresh
        this.user = data.user

        localStorage.setItem('token', this.token)
        localStorage.setItem('refreshToken', this.refreshToken)
        localStorage.setItem('auth_user', JSON.stringify(data.user))
        
        if (data.must_change_password) {
          router.push({ name: 'FirstLogin' })
        } else {
          router.push({ name: 'Dashboard' })
        }
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Erro ao fazer login' 
        }
      }
    },
    
    async loadUser() {
      if (!this.token) return

      try {
        this.user = await authService.getCurrentUser()
        localStorage.setItem('auth_user', JSON.stringify(this.user))
      } catch (error) {
        this.logout()
      }
    },

    async refreshAccessToken() {
      if (!this.refreshToken) return null
      try {
        const data = await authService.refreshToken(this.refreshToken)
        this.token = data.access
        if (data.refresh) this.refreshToken = data.refresh
        localStorage.setItem('token', this.token)
        localStorage.setItem('refreshToken', this.refreshToken)
        return this.token
      } catch {
        return null
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('auth_user')
      import('@/stores/subscription').then(({ useSubscriptionStore }) => {
        useSubscriptionStore().reset()
      }).catch(() => {})
      router.push({ name: 'Login' })
    },
  },
})
