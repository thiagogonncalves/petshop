<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Controle de Usuários</h1>
      </div>
      <router-link
        to="/admin/users/new"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors"
      >
        Novo Usuário
      </router-link>
    </div>

    <div class="mb-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar por nome, usuário ou e-mail..."
        class="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        @input="onSearchInput"
      />
    </div>

    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Usuário</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Perfil</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="u in users" :key="u.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ u.username }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ u.full_name || u.email || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ u.role_display }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ u.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <router-link :to="{ name: 'AdminUserEdit', params: { id: u.id } }"
                          class="text-blue-600 hover:text-blue-800 mr-4">Editar</router-link>
              <button @click="toggleActive(u)" class="text-orange-600 hover:text-orange-800 mr-4">
                {{ u.is_active ? 'Desativar' : 'Ativar' }}
              </button>
              <button @click="openResetPassword(u)" class="text-gray-600 hover:text-gray-800">Redefinir senha</button>
            </td>
          </tr>
          <tr v-if="users.length === 0 && !loading">
            <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum usuário encontrado</td>
          </tr>
        </tbody>
      </table>
      <Pagination
        v-if="pagination && pagination.total_pages > 1"
        :current-page="pagination.current_page"
        :total-pages="pagination.total_pages"
        :total-items="pagination.total_items"
        :items-per-page="pagination.items_per_page"
        @page-change="loadUsers"
      />
    </div>

    <!-- Modal Redefinir senha -->
    <div v-if="showPasswordModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showPasswordModal = false">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-2">Redefinir senha</h3>
        <p class="text-sm text-gray-600 mb-4">Usuário: {{ resetPasswordUser?.username }}</p>
        <input v-model="newPassword" type="password" placeholder="Nova senha"
               class="w-full px-3 py-2 border border-gray-300 rounded-lg mb-2">
        <input v-model="newPasswordConfirm" type="password" placeholder="Confirmar senha"
               class="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4">
        <p v-if="passwordError" class="text-sm text-red-600 mb-2">{{ passwordError }}</p>
        <div class="flex justify-end gap-2">
          <button type="button" @click="showPasswordModal = false" class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-50">Cancelar</button>
          <button type="button" @click="submitResetPassword" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { adminUsersService } from '@/services/adminUsers'
import Pagination from '@/components/Pagination.vue'

const route = useRoute()
const users = ref([])
const loading = ref(false)
const searchQuery = ref('')
const pagination = ref(null)
const showPasswordModal = ref(false)
const resetPasswordUser = ref(null)
const newPassword = ref('')
const newPasswordConfirm = ref('')
const passwordError = ref('')

let searchDebounce = null
function onSearchInput() {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => loadUsers(1), 300)
}

function buildPagination(response) {
  const data = response.data
  if (!data || !('count' in data)) return null
  const total = data.count
  const pageSize = Number(route.query.page_size) || 20
  const page = Number(route.query.page) || 1
  const totalPages = Math.ceil(total / pageSize) || 1
  return {
    current_page: page,
    total_pages: totalPages,
    total_items: total,
    items_per_page: pageSize,
  }
}

async function loadUsers(page = 1) {
  loading.value = true
  try {
    const params = { page, page_size: 20 }
    if (searchQuery.value.trim()) params.q = searchQuery.value.trim()
    const response = await adminUsersService.listUsers(params)
    users.value = response.data.results ?? response.data
    pagination.value = buildPagination(response)
  } catch (err) {
    users.value = []
    if (err.response?.status === 403) {
      alert('Acesso negado. Apenas administradores.')
      return
    }
    console.error(err)
    alert('Erro ao carregar usuários')
  } finally {
    loading.value = false
  }
}

async function toggleActive(user) {
  if (!confirm(`Deseja ${user.is_active ? 'desativar' : 'ativar'} o usuário ${user.username}?`)) return
  try {
    await adminUsersService.toggleActive(user.id)
    await loadUsers(pagination.value?.current_page || 1)
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao alterar status')
  }
}

function openResetPassword(user) {
  resetPasswordUser.value = user
  newPassword.value = ''
  newPasswordConfirm.value = ''
  passwordError.value = ''
  showPasswordModal.value = true
}

async function submitResetPassword() {
  passwordError.value = ''
  if (newPassword.value.length < 8) {
    passwordError.value = 'Senha deve ter no mínimo 8 caracteres.'
    return
  }
  if (newPassword.value !== newPasswordConfirm.value) {
    passwordError.value = 'As senhas não coincidem.'
    return
  }
  try {
    await adminUsersService.setPassword(resetPasswordUser.value.id, newPassword.value)
    showPasswordModal.value = false
    alert('Senha alterada com sucesso.')
  } catch (err) {
    passwordError.value = err.response?.data?.password?.[0] || err.response?.data?.detail || 'Erro ao alterar senha'
  }
}

onMounted(() => loadUsers(1))
watch(() => route.query.page, (p) => { if (p) loadUsers(Number(p)) })
</script>
