import api from './api'

export const settingsService = {
  getBusinessHours() {
    return api.get('/settings/business-hours/')
  },
  updateBusinessHours(data) {
    return api.put('/settings/business-hours/', data)
  },
  getClosures(params = {}) {
    return api.get('/settings/closures/', { params })
  },
  addClosure(data) {
    return api.post('/settings/closures/', data)
  },
  deleteClosure(id) {
    return api.delete(`/settings/closures/${id}/`)
  },
}
