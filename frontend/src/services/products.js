import api from './api'

export const productsService = {
  getAll(params = {}) {
    return api.get('/products/products/', { params })
  },
  
  getById(id) {
    return api.get(`/products/products/${id}/`)
  },
  
  create(data) {
    return api.post('/products/products/', data)
  },
  
  update(id, data) {
    return api.patch(`/products/products/${id}/`, data)
  },
  
  delete(id) {
    return api.delete(`/products/products/${id}/`)
  },
  
  getLowStock() {
    return api.get('/products/products/low_stock/')
  },
  
  getCategories() {
    return api.get('/products/categories/')
  },
  
  createCategory(data) {
    return api.post('/products/categories/', data)
  },
}
