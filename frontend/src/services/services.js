import api from './api'

export const servicesService = {
  getAll(params = {}) {
    return api.get('/services/', { params })
  },
  
  getById(id) {
    return api.get(`/services/${id}/`)
  },
  
  create(data) {
    return api.post('/services/', data)
  },
  
  update(id, data) {
    return api.patch(`/services/${id}/`, data)
  },
  
  delete(id) {
    return api.delete(`/services/${id}/`)
  },
}
