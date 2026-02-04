import api from './api'

export const subscriptionService = {
  getStatus() {
    return api.get('/subscription/status/')
  },

  pay() {
    return api.post('/subscription/pay/')
  },
}
