import { defineStore } from 'pinia'
import { authService } from '@/services/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    userRole: (state) => state.user?.role,
    isAdmin: (state) => state.user?.role === 'admin',
    isManager: (state) => state.user?.role === 'manager' || state.user?.role === 'admin',
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
        
        router.push({ name: 'Dashboard' })
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
      } catch (error) {
        this.logout()
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      router.push({ name: 'Login' })
    },
  },
})
