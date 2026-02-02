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
  
  getCategories(params = {}) {
    return api.get('/products/categories/', { params })
  },

  createCategory(data) {
    return api.post('/products/categories/', data)
  },

  updateCategory(id, data) {
    return api.patch(`/products/categories/${id}/`, data)
  },

  deleteCategory(id) {
    return api.delete(`/products/categories/${id}/`)
  },

  updatePricing(id, data) {
    return api.patch(`/products/products/${id}/pricing/`, data)
  },

  /** PDV: search by name/SKU/GTIN */
  search(q) {
    return api.get('/products/products/search/', { params: { q: q || '' } })
  },

  /** PDV: get product by code (SKU or GTIN) */
  byCode(code) {
    return api.get('/products/products/by-code/', { params: { code: code || '' } })
  },
}
