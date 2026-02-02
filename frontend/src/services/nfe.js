import api from './api'

export const nfeService = {
  importXml(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/nfe/import-xml/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  importByKey(accessKey) {
    return api.post('/nfe/import-by-key/', { access_key: String(accessKey).replace(/\D/g, '') })
  },

  list(params = {}) {
    return api.get('/nfe/', { params })
  },

  getById(id) {
    return api.get(`/nfe/${id}/`)
  },

  confirm(importId, items) {
    return api.post(`/nfe/${importId}/confirm/`, { items })
  },
}
