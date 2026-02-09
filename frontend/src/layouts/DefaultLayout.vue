<template>
  <div
    class="min-h-screen flex flex-col"
    :class="{ 'receipt-print-page': isReceiptPage }"
  >
    <!-- Navigation (fixa como o rodapé) -->
    <nav class="fixed top-0 left-0 right-0 z-30 theme-nav shadow-lg no-print-nav">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14 sm:h-16">
          <div class="flex items-center gap-2">
            <!-- Hamburger (mobile) -->
            <button
              type="button"
              class="sm:hidden p-2 -ml-2 rounded-lg text-white hover:bg-white/20 touch-manipulation"
              aria-label="Abrir menu"
              @click="mobileMenuOpen = !mobileMenuOpen"
            >
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path v-if="!mobileMenuOpen" fill-rule="evenodd" d="M3 5a1 1 0 011-1h16a1 1 0 110 2H4a1 1 0 01-1-1zm0 6a1 1 0 011-1h16a1 1 0 110 2H4a1 1 0 01-1-1zm0 6a1 1 0 011-1h16a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                <path v-else fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
              </svg>
            </button>
            <div class="flex-shrink-0 flex items-center">
              <router-link to="/" class="flex items-center" @click="mobileMenuOpen = false">
                <img v-if="companyStore.logoUrl" :src="companyStore.logoUrl" :alt="companyStore.companyName" class="h-10 sm:h-14 w-auto max-w-[140px] sm:max-w-[200px] object-contain" />
                <img v-else src="@/assets/logosemfundo.png" alt="GB PET" class="h-10 sm:h-14 w-auto" />
              </router-link>
            </div>
            <div class="hidden sm:ml-4 sm:flex sm:items-center sm:space-x-1">
              <template v-for="item in menuItems" :key="item.name">
                <!-- Item simples (link) -->
                <router-link
                  v-if="item.type !== 'dropdown'"
                  :to="item.path"
                  class="theme-nav-link border-transparent text-white inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium transition-colors rounded-t-lg"
                  exact-active-class="theme-nav-link-active"
                >
                  {{ item.name }}
                </router-link>
                <!-- Dropdown Cadastro -->
                <div
                  v-else
                  class="relative group"
                >
                  <span
                    class="theme-nav-link border-transparent text-white inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium transition-colors rounded-t-lg cursor-pointer"
                    :class="{ 'theme-nav-link-active': isCadastroActive || (item.name === 'Crediário' && isCreditsActive) || (item.name === 'Relatórios' && isReportsActive) || (item.name === 'Administração' && isAdminActive) }"
                  >
                    {{ item.name }}
                    <svg class="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                  </span>
                  <div
                    class="absolute left-0 top-full pt-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50"
                  >
                    <div class="py-1 bg-white rounded-lg shadow-lg border-2 theme-card min-w-[160px]">
                      <router-link
                        v-for="child in item.children"
                        :key="child.name"
                        :to="{ path: child.path, query: child.query || {} }"
                        class="block px-4 py-2 text-sm text-gray-700 theme-dropdown-link"
                        active-class="theme-dropdown-link active font-medium"
                      >
                        {{ child.name }}
                      </router-link>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
          <div class="flex items-center gap-1 sm:gap-4">
            <span class="hidden sm:inline text-sm text-white font-medium truncate max-w-[100px] lg:max-w-none">{{ userDisplayName }}</span>
            <button
              @click="logout"
              class="text-sm text-white theme-nav-btn px-3 py-2 rounded-lg touch-manipulation min-h-[44px] sm:min-h-0"
            >
              Sair
            </button>
          </div>
        </div>
      </div>

      <!-- Menu mobile (drawer) -->
      <Transition name="slide">
        <div
          v-show="mobileMenuOpen"
          class="sm:hidden absolute top-full left-0 right-0 bg-white/95 backdrop-blur shadow-xl border-b-2 theme-card max-h-[calc(100vh-3.5rem)] overflow-y-auto"
        >
          <div class="py-2">
            <template v-for="item in menuItems" :key="item.name">
              <router-link
                v-if="item.type !== 'dropdown'"
                :to="item.path"
                class="block px-4 py-3 text-gray-800 font-medium hover:bg-orange-50 border-l-4 border-transparent theme-dropdown-link"
                :class="{ 'theme-dropdown-link active border-l-orange-500 bg-orange-50': route.path === item.path }"
                @click="mobileMenuOpen = false"
              >
                {{ item.name }}
              </router-link>
              <div v-else>
                <div class="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">{{ item.name }}</div>
                <router-link
                  v-for="child in item.children"
                  :key="child.name"
                  :to="{ path: child.path, query: child.query || {} }"
                  class="block px-6 py-2.5 text-sm text-gray-700 hover:bg-orange-50"
                  :class="{ 'font-medium theme-accent-text bg-orange-50': route.path.startsWith(child.path) }"
                  @click="mobileMenuOpen = false"
                >
                  {{ child.name }}
                </router-link>
              </div>
            </template>
          </div>
        </div>
      </Transition>
    </nav>

    <!-- Overlay quando menu mobile aberto -->
    <div
      v-show="mobileMenuOpen"
      class="sm:hidden fixed inset-0 bg-black/40 z-[25] top-14 touch-manipulation"
      aria-hidden="true"
      @click="mobileMenuOpen = false"
    />

    <!-- Main content (padding-top para nav fixa, padding-bottom para rodapé fixo) -->
    <main class="max-w-7xl mx-auto pt-20 sm:pt-24 py-4 sm:py-6 px-3 sm:px-6 lg:px-8 flex-1 w-full no-print-main pb-24 sm:pb-20">
      <RouterView />
    </main>

    <!-- Footer fixo no final da tela -->
    <footer class="fixed bottom-0 left-0 right-0 z-30 theme-footer no-print-footer safe-area-bottom">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-2 sm:py-3">
        <div class="flex flex-row items-center justify-center gap-2 sm:gap-6 flex-wrap text-white text-xs sm:text-sm">
          <router-link to="/" class="flex items-center flex-shrink-0 hidden sm:flex">
            <img v-if="companyStore.logoUrl" :src="companyStore.logoUrl" :alt="companyStore.companyName" class="h-6 sm:h-10 w-auto max-w-[80px] sm:max-w-[120px] object-contain" />
            <img v-else src="@/assets/logosemfundo.png" alt="GB PET" class="h-6 sm:h-10 w-auto" />
          </router-link>
          <span class="font-semibold whitespace-nowrap">{{ currentDateStr }}</span>
          <span class="text-white/70 hidden sm:inline">|</span>
          <span class="font-mono whitespace-nowrap">{{ currentTime }}</span>
          <span class="text-white/70 hidden md:inline">|</span>
          <span class="whitespace-nowrap hidden md:inline">2Cliques Soluções Digitais</span>
          <span class="text-white/70">|</span>
          <span class="whitespace-nowrap">v{{ version }}</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { useSubscriptionStore } from '@/stores/subscription'
import packageJson from '../../package.json'

const subscriptionStore = useSubscriptionStore()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const companyStore = useCompanyStore()
const mobileMenuOpen = ref(false)
const isMobile = ref(typeof window !== 'undefined' && window.innerWidth < 640)
const isReceiptPage = computed(() => route.name === 'ReceiptPrint')
const version = packageJson.version

const currentTime = ref('')
const currentDateStr = ref('')

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentDateStr.value = now.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

let clockTimer = null
function onKeydown(e) {
  if (e.key === 'F2') {
    e.preventDefault()
    router.push({ path: '/pdv' })
  }
}
function updateMobile() {
  isMobile.value = window.innerWidth < 640
}
onMounted(() => {
  updateClock()
  updateMobile()
  clockTimer = setInterval(updateClock, 1000)
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', updateMobile)
  companyStore.fetchCompany()
  subscriptionStore.fetchStatus().catch(() => {})
})
onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', updateMobile)
})

const user = computed(() => authStore.user)
const userDisplayName = computed(() => {
  const u = authStore.user
  if (!u) return ''
  const full = u.full_name || [u.first_name, u.last_name].filter(Boolean).join(' ').trim()
  return full || u.username || u.email || ''
})

const isCadastroActive = computed(() => {
  const cadastroPaths = ['/clients', '/pets', '/products', '/services']
  return cadastroPaths.some(p => route.path.startsWith(p))
})

const isCreditsActive = computed(() => route.path.startsWith('/credits'))
const isReportsActive = computed(() => route.path.startsWith('/reports'))
const isAdminActive = computed(() => route.path.startsWith('/admin'))

const menuItems = computed(() => {
  const items = [
    { name: 'Dashboard', path: '/' },
    {
      type: 'dropdown',
      name: 'Cadastro',
      children: [
        { name: 'Clientes', path: '/clients' },
        { name: 'Pets', path: '/pets' },
        { name: 'Produtos', path: '/products' },
        { name: 'Categorias', path: '/categories' },
        { name: 'Serviços', path: '/services' },
      ],
    },
    { name: 'Agendamentos', path: '/scheduling' },
    { name: 'PDV', path: '/pdv', hideOnMobile: true },
    { name: 'Crediário', path: '/credits' },
  ]
  
  if (authStore.isAuthenticated) {
    items.push({
      type: 'dropdown',
      name: 'Relatórios',
      children: [
        { name: 'Dashboard', path: '/reports/dashboard' },
        { name: 'Vendas', path: '/reports/sales' },
        { name: 'Produtos Vendidos', path: '/reports/products-sold' },
        { name: 'Ranking de Vendedores', path: '/reports/ranking' },
        { name: 'Estoque Baixo', path: '/reports/low-stock' },
        { name: 'Top Clientes', path: '/reports/top-clients' },
      ],
    })
  }

  if (authStore.isAdmin) {
    items.push({
      type: 'dropdown',
      name: 'Administração',
      children: [
        { name: 'Plano e Pagamento', path: '/admin/plan' },
        { name: 'Dados da empresa', path: '/admin/company' },
        { name: 'Usuários', path: '/admin/users' },
        { name: 'Perfis e Permissões', path: '/admin/roles' },
        { name: 'Logs de Acesso', path: '/admin/audit' },
        { name: 'Configurações', path: '/admin/settings' },
      ],
    })
  }
  
  return items.filter(item => !(isMobile.value && item.hideOnMobile))
})

const logout = () => {
  authStore.logout()
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
<style>
@media print {
  .receipt-print-page .no-print-nav,
  .receipt-print-page .no-print-footer {
    display: none !important;
  }
  .receipt-print-page .no-print-main {
    padding: 0 !important;
    max-width: none !important;
  }
}
</style>