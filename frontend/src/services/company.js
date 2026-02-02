import api from './api'

/** Dados da empresa (público: login, PDV, cupom) */
export const companyService = {
  get() {
    return api.get('/auth/company/')
  },
}

/** Admin: dados da empresa (edição) */
export const adminCompanyService = {
  async get() {
    const res = await api.get('/admin/company-settings/')
    const raw = res.data
    const list = raw?.results ?? (Array.isArray(raw) ? raw : [raw])
    const first = list?.length ? list[0] : (raw?.id ? raw : null)
    return { data: first ?? {} }
  },

  update(id, payload) {
    return api.patch(`/admin/company-settings/${id}/`, payload)
  },
}
