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
          path: 'reports',
          name: 'Reports',
          component: () => import('@/views/Reports.vue'),
        },
      ]
    },
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
