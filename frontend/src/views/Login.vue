<template>
  <div class="min-h-screen flex items-center justify-center theme-login-bg py-4 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Paw Prints Background -->
    <div class="absolute inset-0 opacity-20">
      <svg class="absolute top-20 left-20 w-16 h-16 theme-accent-fill" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
      <svg class="absolute top-40 right-32 w-12 h-12 theme-accent-fill" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
      <svg class="absolute bottom-32 left-32 w-14 h-14 theme-accent-fill" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
      <svg class="absolute top-60 right-20 w-10 h-10 theme-accent-fill" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
    </div>
    
    <div class="max-w-md w-full relative z-10">
      <div class="bg-white rounded-xl shadow-2xl p-5">
        <!-- Logo e Título (dados da empresa) -->
        <div class="text-center mb-4">
          <div class="flex items-center justify-center mb-2">
            <img v-if="company.logo_url" :src="mediaUrl(company.logo_url)" :alt="company.name || 'Logo'" class="w-28 h-28 object-contain" />
            <img v-else src="@/assets/logosemfundo.png" alt="GB PET" class="w-28 h-28 object-contain" />
          </div>
          <p v-if="company.name" class="text-gray-800 font-semibold text-base">{{ company.name }}</p>
          <p v-if="company.cpf_cnpj" class="text-gray-600 text-xs">{{ company.cpf_cnpj }}</p>
          <p class="text-sm font-medium mt-0.5 theme-accent-text">Sistema de Gestão para Pet Shop</p>
        </div>

        <!-- Formulário -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Usuário</label>
            <input
              id="username"
              v-model="username"
              name="username"
              type="text"
              required
              placeholder="admin"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 theme-input-focus text-gray-700 placeholder-gray-400"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              required
              placeholder="********"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 theme-input-focus text-gray-700 placeholder-gray-400"
            />
          </div>

          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {{ error }}
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg text-white theme-btn-primary focus:outline-none focus:ring-2 focus:ring-offset-2 font-medium text-sm transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg theme-focus-ring"
            >
              {{ loading ? 'Entrando...' : 'Entrar' }}
            </button>
          </div>
        </form>

        <!-- Instruções de primeiro acesso (visível até o admin trocar a senha) -->
        <div v-if="showFirstLoginInstructions" class="mt-4 pt-4 border-t-2 theme-card text-center">
          <p class="text-xs text-gray-600 font-medium">Primeiro acesso:</p>
          <p class="text-xs text-gray-600 font-medium mt-1">Usuário: admin</p>
          <p class="text-xs text-gray-600 font-medium">Senha: admin</p>
          <p class="text-xs text-amber-600 mt-2 font-medium">Altere usuário e senha no primeiro login.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { companyService } from '@/services/company'
import { mediaUrl } from '@/utils/mediaUrl'

const authStore = useAuthStore()
const company = ref({})
const showFirstLoginInstructions = ref(true)

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await companyService.get()
    company.value = data || {}
    showFirstLoginInstructions.value = data?.show_first_login_instructions !== false
    document.title = (data?.name || 'GB PET')
    document.body.setAttribute('data-theme', data?.theme || 'orange')
  } catch {
    company.value = {}
    showFirstLoginInstructions.value = true
  }
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  const result = await authStore.login(username.value, password.value)
  
  if (!result.success) {
    error.value = result.error
  }
  
  loading.value = false
}
</script>