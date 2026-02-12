import api from './api'

export const fiscalService = {
  getConfig() {
    return api.get('/fiscal/config/')
  },

  saveConfig(formData) {
    return api.post('/fiscal/config/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  importByKey(accessKey) {
    return api.post('/fiscal/nfe/import-by-key/', {
      access_key: String(accessKey).replace(/\D/g, ''),
    })
  },

  sync() {
    return api.post('/fiscal/nfe/sync/')
  },

  listNFe(params = {}) {
    return api.get('/fiscal/nfe/', { params })
  },

  getNFeById(id) {
    return api.get(`/fiscal/nfe/${id}/`)
  },

  getNFeXmlUrl(id) {
    return `/api/fiscal/nfe/${id}/xml/`
  },
}
