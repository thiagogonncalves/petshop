<template>
  <div>
    <div class="flex items-center mb-6">
      <router-link to="/admin/users" class="text-blue-600 hover:text-blue-800 mr-4">← Voltar</router-link>
      <h1 class="text-2xl font-bold text-blue-800">Novo Usuário</h1>
    </div>

    <div class="bg-white shadow-lg rounded-lg border-2 theme-card p-6 max-w-2xl">
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
            <label class="block text-sm font-medium text-gray-700 mb-1">Senha inicial *</label>
            <input v-model="form.password" type="password" required minlength="8"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                   placeholder="Mínimo 8 caracteres">
            <p v-if="errors.password" class="text-sm text-red-600 mt-1">{{ errors.password }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar senha *</label>
            <input v-model="form.password_confirm" type="password" required
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
            <p v-if="errors.password_confirm" class="text-sm text-red-600 mt-1">{{ errors.password_confirm }}</p>
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
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Criar usuário</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminUsersService } from '@/services/adminUsers'

const router = useRouter()
const formError = ref('')
const errors = ref({})
const roleOptions = ref([])
const form = reactive({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'user',
  phone: '',
  is_active: true,
})

onMounted(async () => {
  try {
    const { data } = await adminUsersService.listRoleOptions()
    roleOptions.value = Array.isArray(data) ? data : []
  } catch {
    roleOptions.value = []
  }
})

function validate() {
  errors.value = {}
  if (form.password.length < 8) errors.value.password = 'Senha deve ter no mínimo 8 caracteres.'
  if (form.password !== form.password_confirm) errors.value.password_confirm = 'As senhas não coincidem.'
  return Object.keys(errors.value).length === 0
}

async function save() {
  formError.value = ''
  errors.value = {}
  if (!validate()) return
  const phone = (form.phone || '').replace(/\D/g, '')
  const roleValue = form.role
  const isCustomRole = String(roleValue).startsWith('role_')
  const payload = {
    username: form.username.trim(),
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    email: form.email.trim(),
    password: form.password,
    password_confirm: form.password_confirm,
    role: isCustomRole ? 'user' : roleValue,
    is_active: form.is_active,
  }
  if (isCustomRole) payload.custom_role = parseInt(roleValue.replace('role_', ''), 10)
  else payload.custom_role = null
  if (phone.length >= 9) payload.phone = phone
  try {
    await adminUsersService.createUser(payload)
    alert('Usuário criado com sucesso.')
    router.push({ name: 'AdminUsersList' })
  } catch (err) {
    const data = err.response?.data || {}
    errors.value = {}
    if (data && typeof data === 'object') {
      Object.keys(data).forEach(k => {
        const msg = Array.isArray(data[k]) ? data[k][0] : data[k]
        errors.value[k] = typeof msg === 'string' ? msg : JSON.stringify(msg)
      })
      const msgParts = Object.entries(errors.value).map(([k, v]) => `${k}: ${v}`)
      formError.value = typeof data.detail === 'string' ? data.detail : (msgParts.length ? msgParts.join(' • ') : err.message || 'Erro ao criar usuário')
    } else {
      formError.value = err.message || 'Erro ao criar usuário'
    }
  }
}
</script>
