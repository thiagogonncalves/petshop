import api from './api'

export const petsService = {
  getAll(params = {}) {
    return api.get('/pets/', { params })
  },
  
  getById(id) {
    return api.get(`/pets/${id}/`)
  },
  
  create(data) {
    const headers = { 'Content-Type': 'multipart/form-data' }
    return api.post('/pets/', data, { headers })
  },
  
  update(id, data) {
    const headers = { 'Content-Type': 'multipart/form-data' }
    return api.patch(`/pets/${id}/`, data, { headers })
  },
  
  delete(id) {
    return api.delete(`/pets/${id}/`)
  },
  
  getCard(id) {
    return api.get(`/pets/${id}/card/`, { responseType: 'blob' })
  },
}
