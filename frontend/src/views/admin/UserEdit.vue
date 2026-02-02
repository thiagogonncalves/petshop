<template>
  <div>
    <div class="flex items-center mb-6">
      <router-link to="/admin/users" class="text-blue-600 hover:text-blue-800 mr-4">← Voltar</router-link>
      <h1 class="text-2xl font-bold text-blue-800">Editar Usuário</h1>
    </div>

    <div v-if="loading" class="text-center text-gray-500">Carregando...</div>
    <div v-else class="bg-white shadow-lg rounded-lg border-2 border-orange-200 p-6 max-w-2xl">
      <form @submit.prevent="save">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome de usuário *</label>
            <input v-model="form.username" type="text" required
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
            <p v-if="errors.username" class="text-sm text-red-600 mt-1">{{ errors.username }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input v-model="form.first_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sobrenome</label>
            <input v-model="form.last_name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">E-mail *</label>
            <input v-model="form.email" type="email" required
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
            <p v-if="errors.email" class="text-sm text-red-600 mt-1">{{ errors.email }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nova senha (deixe em branco para manter)</label>
            <input v-model="form.password" type="password" minlength="8"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                   placeholder="Mínimo 8 caracteres">
            <p v-if="errors.password" class="text-sm text-red-600 mt-1">{{ errors.password }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Perfil *</label>
            <select v-model="form.role" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
              <option value="admin">Administrador</option>
              <option value="manager">Gerente</option>
              <option value="user">Usuário</option>
              <option v-for="r in roleOptions.filter(o => o.type === 'custom')" :key="r.value" :value="r.value">{{ r.label }} (perfil customizado)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
            <input v-model="form.phone" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div class="md:col-span-2">
            <label class="flex items-center gap-2">
              <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
              <span class="text-sm text-gray-700">Ativo</span>
            </label>
          </div>
        </div>
        <p v-if="formError" class="text-sm text-red-600 mb-4">{{ formError }}</p>
        <div class="flex gap-3">
          <router-link to="/admin/users" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">Cancelar</router-link>
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Salvar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminUsersService } from '@/services/adminUsers'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const formError = ref('')
const errors = ref({})
const roleOptions = ref([])
const form = reactive({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  role: 'user',
  phone: '',
  is_active: true,
})

function validate() {
  errors.value = {}
  if (form.password && form.password.length < 8) errors.value.password = 'Senha deve ter no mínimo 8 caracteres.'
  return Object.keys(errors.value).length === 0
}

async function loadUser() {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    const { data } = await adminUsersService.getUser(id)
    form.username = data.username ?? ''
    form.first_name = data.first_name ?? ''
    form.last_name = data.last_name ?? ''
    form.email = data.email ?? ''
    form.role = data.custom_role ? `role_${data.custom_role}` : (data.role ?? 'user')
    form.phone = data.phone ?? ''
    form.is_active = data.is_active ?? true
    form.password = ''
  } catch (err) {
    if (err.response?.status === 404) router.push({ name: 'AdminUsersList' })
    else alert(err.response?.data?.detail || 'Erro ao carregar usuário')
  } finally {
    loading.value = false
  }
}

async function save() {
  formError.value = ''
  errors.value = {}
  if (!validate()) return
  const roleValue = form.role
  const isCustomRole = String(roleValue).startsWith('role_')
  const payload = {
    username: form.username.trim(),
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    email: form.email.trim(),
    role: isCustomRole ? 'user' : roleValue,
    custom_role: isCustomRole ? parseInt(roleValue.replace('role_', ''), 10) : null,
    phone: form.phone || undefined,
    is_active: form.is_active,
  }
  if (form.password) payload.password = form.password
  try {
    await adminUsersService.updateUser(route.params.id, payload)
    alert('Usuário atualizado com sucesso.')
    router.push({ name: 'AdminUsersList' })
  } catch (err) {
    const data = err.response?.data || {}
    if (typeof data === 'object') {
      Object.keys(data).forEach(k => { errors.value[k] = Array.isArray(data[k]) ? data[k][0] : data[k] })
    }
    formError.value = data.detail || err.message || 'Erro ao atualizar usuário'
  }
}

onMounted(async () => {
  try {
    const { data } = await adminUsersService.listRoleOptions()
    roleOptions.value = Array.isArray(data) ? data : []
  } catch {
    roleOptions.value = []
  }
  await loadUser()
})
watch(() => route.params.id, () => loadUser())
</script>
