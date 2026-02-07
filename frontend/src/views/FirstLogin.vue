<template>
  <div class="min-h-screen flex items-center justify-center theme-login-bg py-4 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-xl shadow-2xl p-6">
      <h1 class="text-xl font-bold text-gray-800 mb-2">Alterar credenciais de acesso</h1>
      <p class="text-sm text-gray-600 mb-6">
        Esta é a primeira vez que você acessa o sistema. Defina seu usuário (e-mail) e senha para continuar.
      </p>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="new_username" class="block text-sm font-medium text-gray-700 mb-1">Novo usuário</label>
          <input
            id="new_username"
            v-model="newUsername"
            type="text"
            required
            placeholder="usuário ou e-mail"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 theme-input-focus text-gray-700 placeholder-gray-400"
          />
        </div>

        <div>
          <label for="new_password" class="block text-sm font-medium text-gray-700 mb-1">Nova senha</label>
          <input
            id="new_password"
            v-model="newPassword"
            type="password"
            required
            placeholder="********"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 theme-input-focus text-gray-700 placeholder-gray-400"
          />
          <p class="text-xs text-gray-500 mt-1">Mínimo 8 caracteres. Use letras, números e símbolos.</p>
        </div>

        <div>
          <label for="new_password_confirm" class="block text-sm font-medium text-gray-700 mb-1">Confirmar nova senha</label>
          <input
            id="new_password_confirm"
            v-model="newPasswordConfirm"
            type="password"
            required
            placeholder="********"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 theme-input-focus text-gray-700 placeholder-gray-400"
          />
        </div>

        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg text-white theme-btn-primary focus:outline-none focus:ring-2 focus:ring-offset-2 font-medium text-sm transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg theme-focus-ring"
        >
          {{ loading ? 'Salvando...' : 'Salvar e continuar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth'
import router from '@/router'

const authStore = useAuthStore()

const newUsername = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const loading = ref(false)
const error = ref('')

function getErrorMessage(err) {
  const d = err.response?.data
  if (!d) return 'Erro ao salvar.'
  if (typeof d === 'string') return d
  const msg = d.detail || d.new_username?.[0] || d.new_password?.[0] || d.new_password_confirm?.[0]
  return msg || 'Erro ao salvar.'
}

async function handleSubmit() {
  if (newPassword.value !== newPasswordConfirm.value) {
    error.value = 'As senhas não coincidem.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const data = await authService.firstLoginChangePassword(
      newUsername.value,
      newPassword.value,
      newPasswordConfirm.value
    )
    authStore.token = data.access
    authStore.refreshToken = data.refresh
    authStore.user = data.user
    localStorage.setItem('token', data.access)
    localStorage.setItem('refreshToken', data.refresh)
    router.push({ name: 'Dashboard' })
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>
