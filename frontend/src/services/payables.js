import api from './api'

export const payablesService = {
  getAll(params = {}) {
    return api.get('/payables/', { params })
  },

  getById(id) {
    return api.get(`/payables/${id}/`)
  },

  create(data) {
    return api.post('/payables/', data)
  },

  update(id, data) {
    return api.patch(`/payables/${id}/`, data)
  },

  delete(id) {
    return api.delete(`/payables/${id}/`)
  },

  getAlerts() {
    return api.get('/payables/alerts/')
  },

  markPaid(id, paidDate = null) {
    return api.post(`/payables/${id}/mark_paid/`, paidDate ? { paid_date: paidDate } : {})
  },
}
