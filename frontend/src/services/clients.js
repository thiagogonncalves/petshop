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

  /** PDV: get client by CPF (digits only) */
  byCpf(cpf) {
    return api.get('/clients/by-cpf/', { params: { cpf: cpf || '' } })
  },

  /** Histórico de crediários do cliente */
  getCredits(clientId) {
    return api.get(`/clients/${clientId}/credits/`)
  },
}
