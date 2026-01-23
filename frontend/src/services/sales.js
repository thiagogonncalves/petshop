import api from './api'

export const salesService = {
  getAll(params = {}) {
    return api.get('/sales/sales/', { params })
  },
  
  getById(id) {
    return api.get(`/sales/sales/${id}/`)
  },
  
  create(data) {
    return api.post('/sales/sales/', data)
  },
  
  update(id, data) {
    return api.patch(`/sales/sales/${id}/`, data)
  },
  
  completePayment(id) {
    return api.post(`/sales/sales/${id}/complete_payment/`)
  },
  
  generateReceipt(id) {
    return api.post(`/sales/sales/${id}/generate_receipt/`)
  },
  
  generateInvoice(id) {
    return api.post(`/sales/sales/${id}/generate_invoice/`)
  },
}
