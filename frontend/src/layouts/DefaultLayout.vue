<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-white to-blue-50 flex flex-col">
    <!-- Navigation -->
    <nav class="bg-gradient-to-r from-orange-500 to-orange-400 shadow-lg border-b-4 border-blue-500">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <div class="flex items-center space-x-3">
                <svg class="w-10 h-10 text-blue-700" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
                <svg class="w-10 h-10 text-blue-700 -ml-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
                <h1 class="text-2xl font-bold text-blue-800">Happy Pets</h1>
              </div>
            </div>
            <div class="hidden sm:ml-8 sm:flex sm:space-x-6">
              <router-link
                v-for="item in menuItems"
                :key="item.name"
                :to="item.path"
                class="border-transparent text-white hover:text-blue-100 hover:bg-orange-600 inline-flex items-center px-3 pt-1 border-b-2 text-sm font-medium transition-colors rounded-t-lg"
                active-class="border-blue-800 text-white bg-orange-600"
              >
                {{ item.name }}
              </router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-white font-medium">{{ user?.username || user?.email }}</span>
            <button
              @click="logout"
              class="text-sm text-white hover:text-blue-100 transition-colors bg-orange-600 hover:bg-orange-700 px-3 py-1 rounded-lg"
            >
              Sair
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 flex-1 w-full">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="bg-gradient-to-r from-orange-500 to-orange-400 border-t-4 border-blue-500 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-col sm:flex-row justify-between items-center text-white">
          <div class="flex items-center mb-2 sm:mb-0">
            <span class="text-sm font-medium">Desenvolvido por</span>
            <span class="ml-2 text-base font-bold">2Cliques</span>
          </div>
          <div class="text-sm">
            <span class="font-medium">Versão</span>
            <span class="ml-2">{{ version }}</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import packageJson from '../../package.json'

const authStore = useAuthStore()
const version = packageJson.version

const user = computed(() => authStore.user)

const menuItems = computed(() => {
  const items = [
    { name: 'Dashboard', path: '/' },
    { name: 'Clientes', path: '/clients' },
    { name: 'Animais', path: '/pets' },
    { name: 'Produtos', path: '/products' },
    { name: 'Serviços', path: '/services' },
    { name: 'Agendamentos', path: '/scheduling' },
    { name: 'Vendas', path: '/sales' },
  ]
  
  if (authStore.isManager) {
    items.push({ name: 'Relatórios', path: '/reports' })
  }
  
  return items
})

const logout = () => {
  authStore.logout()
}
</script>