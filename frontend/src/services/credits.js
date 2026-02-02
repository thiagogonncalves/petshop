import api from './api'

export const creditsService = {
  getAll(params = {}) {
    return api.get('/credits/', { params })
  },

  getById(id) {
    return api.get(`/credits/${id}/`)
  },

  getForecast(params = {}) {
    return api.get('/credits/forecast/', { params })
  },

  payInstallment(installmentId, data = {}) {
    return api.post(`/credits/installments/${installmentId}/pay/`, data)
  },
}
