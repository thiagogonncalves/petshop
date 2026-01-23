import api from './api'

export const schedulingService = {
  getAll(params = {}) {
    return api.get('/scheduling/', { params })
  },
  
  getById(id) {
    return api.get(`/scheduling/${id}/`)
  },
  
  create(data) {
    return api.post('/scheduling/', data)
  },
  
  update(id, data) {
    return api.patch(`/scheduling/${id}/`, data)
  },
  
  delete(id) {
    return api.delete(`/scheduling/${id}/`)
  },
  
  getToday() {
    return api.get('/scheduling/today/')
  },
  
  getUpcoming() {
    return api.get('/scheduling/upcoming/')
  },
  
  complete(id) {
    return api.post(`/scheduling/${id}/complete/`)
  },
  
  cancel(id) {
    return api.post(`/scheduling/${id}/cancel/`)
  },
}
