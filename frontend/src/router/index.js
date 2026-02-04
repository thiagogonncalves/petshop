import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/agendar',
      name: 'BookAppointment',
      component: () => import('@/views/public/BookAppointment.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/agendar/meus',
      name: 'MyAppointments',
      component: () => import('@/views/public/MyAppointments.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/pdv',
      name: 'PdvSale',
      component: () => import('@/views/PdvSale.vue'),
      meta: { requiresAuth: true, fullscreen: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
        },
        {
          path: 'clients',
          name: 'Clients',
          component: () => import('@/views/Clients.vue'),
        },
        {
          path: 'pets',
          name: 'Pets',
          component: () => import('@/views/Pets.vue'),
        },
        {
          path: 'products',
          name: 'Products',
          component: () => import('@/views/Products.vue'),
        },
        {
          path: 'categories',
          name: 'Categories',
          component: () => import('@/views/Categories.vue'),
        },
        {
          path: 'nfe',
          name: 'ImportNFe',
          component: () => import('@/views/ImportNFe.vue'),
        },
        {
          path: 'services',
          name: 'Services',
          component: () => import('@/views/Services.vue'),
        },
        {
          path: 'scheduling',
          name: 'Scheduling',
          component: () => import('@/views/Scheduling.vue'),
        },
        {
          path: 'sales',
          name: 'Sales',
          component: () => import('@/views/Sales.vue'),
        },
        {
          path: 'credits',
          component: () => import('@/views/credits/CreditsLayout.vue'),
          children: [
            { path: '', name: 'CreditsList', component: () => import('@/views/credits/CreditsList.vue') },
            { path: 'client/:clientId', name: 'ClientCredits', component: () => import('@/views/credits/ClientCredits.vue') },
            { path: ':id', name: 'CreditDetail', component: () => import('@/views/credits/CreditDetail.vue') },
          ],
        },
        {
          path: 'receipt/:id',
          name: 'ReceiptPrint',
          component: () => import('@/views/ReceiptPrint.vue'),
          meta: { requiresAuth: false },
        },
        {
          path: 'reports',
          component: () => import('@/views/reports/ReportsLayout.vue'),
          children: [
            { path: '', redirect: { name: 'ReportsDashboard' } },
            { path: 'dashboard', name: 'ReportsDashboard', component: () => import('@/views/reports/ReportsDashboard.vue') },
            { path: 'sales', name: 'ReportsSales', component: () => import('@/views/reports/ReportsSales.vue') },
            { path: 'products-sold', name: 'ReportsProductsSold', component: () => import('@/views/reports/ReportsProductsSold.vue') },
            { path: 'ranking', name: 'ReportsSalesRanking', component: () => import('@/views/reports/ReportsSalesRanking.vue') },
            { path: 'low-stock', name: 'ReportsLowStock', component: () => import('@/views/reports/ReportsLowStock.vue') },
            { path: 'top-clients', name: 'ReportsTopClients', component: () => import('@/views/reports/ReportsTopClients.vue') },
          ],
        },
        // Administração (somente admin)
        {
          path: 'admin/company',
          name: 'AdminCompanyData',
          component: () => import('@/views/admin/CompanyData.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'admin/plan',
          name: 'AdminPlanPayment',
          component: () => import('@/views/admin/PlanPayment.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'admin/users',
          name: 'AdminUsersList',
          component: () => import('@/views/admin/UsersList.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'admin/users/new',
          name: 'AdminUserCreate',
          component: () => import('@/views/admin/UserCreate.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'admin/users/:id/edit',
          name: 'AdminUserEdit',
          component: () => import('@/views/admin/UserEdit.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'admin/roles',
          name: 'AdminRoles',
          component: () => import('@/views/admin/RolesPermissions.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'admin/audit',
          name: 'AdminAudit',
          component: () => import('@/views/admin/AuditLogs.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'admin/settings',
          name: 'AdminSettings',
          component: () => import('@/views/admin/Settings.vue'),
          meta: { requiresAdmin: true },
        },
      ]
    },
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Se tem token mas user ainda não foi carregado (ex.: após refresh), carrega o usuário
  if (authStore.token && !authStore.user) {
    try {
      await authStore.loadUser()
    } catch {
      authStore.logout()
      next({ name: 'Login' })
      return
    }
  }
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
    return
  }
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard', query: { adminRequired: '1' } })
    return
  }
  next()
})

export default router
