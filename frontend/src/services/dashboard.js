/**
 * Dashboard API — endpoint único agregado
 */
import api from './api'

export const dashboardService = {
  /**
   * GET /api/reports/dashboard-summary/?date=YYYY-MM-DD
   * Retorna KPIs, agenda do dia, alertas, clientes, gráficos e insights.
   */
  getDashboardSummary(params = {}) {
    return api.get('/reports/dashboard-summary/', { params })
  },
}
