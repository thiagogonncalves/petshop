import api from './api'

export const adminUsersService = {
  listUsers(params = {}) {
    return api.get('/admin/users/', { params })
  },

  getUser(id) {
    return api.get(`/admin/users/${id}/`)
  },

  createUser(payload) {
    return api.post('/admin/users/', payload)
  },

  updateUser(id, payload) {
    return api.patch(`/admin/users/${id}/`, payload)
  },

  toggleActive(id) {
    return api.post(`/admin/users/${id}/toggle-active/`)
  },

  setPassword(id, password) {
    return api.post(`/admin/users/${id}/set-password/`, { password })
  },

  listRoles() {
    return api.get('/admin/roles/')
  },

  getRole(id) {
    return api.get(`/admin/roles/${id}/`)
  },

  createRole(payload) {
    return api.post('/admin/roles/', payload)
  },

  updateRole(id, payload) {
    return api.patch(`/admin/roles/${id}/`, payload)
  },

  deleteRole(id) {
    return api.delete(`/admin/roles/${id}/`)
  },

  listPermissions() {
    return api.get('/admin/permissions/')
  },

  listRoleOptions() {
    return api.get('/admin/role-options/')
  },
}
