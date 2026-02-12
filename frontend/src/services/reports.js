import api from './api'

const BASE = 'reports'

/** List of sellers (users with sales) for filter dropdowns */
export function getSellers() {
  return api.get(`${BASE}/sellers/`).then((r) => r.data)
}

/**
 * @param {Object} params - start, end (YYYY-MM-DD), user_id, payment_method, status
 */
export function getDashboard(params = {}) {
  return api.get(`${BASE}/dashboard/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end, user_id, client_id, status, q, page, page_size, include_cancelled
 */
export function getSales(params = {}) {
  return api.get(`${BASE}/sales/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end, category_id, order (qty|revenue|profit), limit
 */
export function getProductsSold(params = {}) {
  return api.get(`${BASE}/products-sold/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end, order (revenue|count|items), limit
 */
export function getSalesRanking(params = {}) {
  return api.get(`${BASE}/sales-ranking/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - threshold (optional)
 */
export function getLowStock(params = {}) {
  return api.get(`${BASE}/low-stock/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end, metric (revenue|qty)
 */
export function getABCProducts(params = {}) {
  return api.get(`${BASE}/abc-products/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end
 */
export function getServicesSold(params = {}) {
  return api.get(`${BASE}/services-sold/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end, order (revenue|count), limit
 */
export function getTopClients(params = {}) {
  return api.get(`${BASE}/top-clients/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end
 */
export function getSalesHeatmap(params = {}) {
  return api.get(`${BASE}/sales-heatmap/`, { params }).then((r) => r.data)
}

/**
 * @param {Object} params - start, end
 */
export function getProfitByProduct(params = {}) {
  return api.get(`${BASE}/profit-by-product/`, { params }).then((r) => r.data)
}

/**
 * Export sales to CSV. Returns blob URL or triggers download.
 * @param {Object} params - start, end, user_id, client_id, status, include_cancelled
 */
export function exportSalesCsv(params = {}) {
  const qs = new URLSearchParams(params).toString()
  const url = `${BASE}/sales/export.csv${qs ? `?${qs}` : ''}`
  return api.get(url, { responseType: 'blob' }).then((response) => {
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = response.headers['content-disposition']?.split('filename=')?.[1]?.replace(/"/g, '') || 'vendas.csv'
    link.click()
    window.URL.revokeObjectURL(link.href)
  })
}

/**
 * Export products sold to CSV.
 * @param {Object} params - start, end, category_id, order
 */
export function exportProductsSoldCsv(params = {}) {
  const qs = new URLSearchParams(params).toString()
  const url = `${BASE}/products-sold/export.csv${qs ? `?${qs}` : ''}`
  return api.get(url, { responseType: 'blob' }).then((response) => {
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = response.headers['content-disposition']?.split('filename=')?.[1]?.replace(/"/g, '') || 'produtos_vendidos.csv'
    link.click()
    window.URL.revokeObjectURL(link.href)
  })
}
