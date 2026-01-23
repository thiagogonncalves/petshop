import api from './api'

export const clientsService = {
  getAll(params = {}) {
    return api.get('/clients/', { params })
  },
  
  getById(id) {
    return api.get(`/clients/${id}/`)
  },
  
  create(data) {
    return api.post('/clients/', data)
  },
  
  update(id, data) {
    return api.patch(`/clients/${id}/`, data)
  },
  
  delete(id) {
    return api.delete(`/clients/${id}/`)
  },
  
  getPets(clientId) {
    return api.get(`/clients/${clientId}/pets/`)
  },
}
