import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: tenta refresh do token antes de deslogar em 401
let isRefreshing = false
let failedQueue = []

function processQueue(err, token = null) {
  failedQueue.forEach((prom) => (err ? prom.reject(err) : prom.resolve(token)))
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401) {
      const isLoginRequest = originalRequest?.url?.includes('login')
      const isRefreshRequest = originalRequest?.url?.includes('token/refresh')
      if (isLoginRequest || isRefreshRequest) {
        const authStore = useAuthStore()
        authStore.logout()
        window.location.href = '/login'
        return Promise.reject(error)
      }
      const authStore = useAuthStore()
      if (!authStore.refreshToken) {
        authStore.logout()
        window.location.href = '/login'
        return Promise.reject(error)
      }
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }).catch((err) => Promise.reject(err))
      }
      originalRequest._retry = true
      isRefreshing = true
      try {
        const newToken = await authStore.refreshAccessToken()
        if (newToken) {
          processQueue(null, newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        }
        throw new Error('Refresh failed')
      } catch (refreshError) {
        processQueue(refreshError, null)
        authStore.logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    if (error.response?.status === 403 && error.response?.data?.detail === 'subscription_expired') {
      import('@/stores/subscription').then(({ useSubscriptionStore }) => {
        const subStore = useSubscriptionStore()
        subStore.canWrite = false
        subStore.status = 'expired'
      })
    }
    return Promise.reject(error)
  }
)

export default api
