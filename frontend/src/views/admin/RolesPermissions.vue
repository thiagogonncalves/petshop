<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Perfis e Permissões</h1>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors"
      >
        Novo Perfil
      </button>
    </div>

    <p class="text-gray-600 mb-4">Crie perfis customizados e escolha quais permissões cada um terá. Os perfis built-in (Administrador, Gerente, Usuário) continuam disponíveis ao cadastrar usuários.</p>

    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 theme-card">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="theme-table-header">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Código</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Permissões</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="role in roles" :key="role.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ role.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ role.code }}</td>
            <td class="px-6 py-4 text-sm text-gray-500">
              <span v-if="role.permissions && role.permissions.length">{{ role.permissions.length }} permissões</span>
              <span v-else class="text-gray-400">Nenhuma</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="openModal(role)" class="text-blue-600 hover:text-blue-800 mr-4">Editar</button>
              <button @click="deleteRole(role)" class="text-red-600 hover:text-red-900">Excluir</button>
            </td>
          </tr>
          <tr v-if="roles.length === 0 && !loading">
            <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum perfil customizado. Crie um com o botão acima.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Novo/Editar Perfil -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto" @click.self="showModal = false">
      <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 my-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">{{ editingRole ? 'Editar Perfil' : 'Novo Perfil' }}</h3>
        <form @submit.prevent="saveRole">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="form.name" type="text" required placeholder="Ex: Atendente"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500">
            <p v-if="errors.name" class="text-sm text-red-600 mt-1">{{ errors.name }}</p>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Código (único) *</label>
            <input v-model="form.code" type="text" required placeholder="Ex: atendente"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                   :disabled="!!editingRole">
            <p class="text-xs text-gray-500 mt-1">Apenas letras minúsculas, números e hífen. Não pode ser alterado após criar.</p>
            <p v-if="errors.code" class="text-sm text-red-600 mt-1">{{ errors.code }}</p>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">O que este perfil pode fazer</label>
            <div class="border border-gray-200 rounded-lg p-4 max-h-64 overflow-y-auto bg-gray-50">
              <label v-for="perm in permissions" :key="perm.code" class="flex items-center gap-2 py-1.5 hover:bg-gray-100 rounded px-2">
                <input v-model="form.permissions" type="checkbox" :value="perm.code"
                       class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                <span class="text-sm text-gray-700">{{ perm.label }}</span>
              </label>
            </div>
            <p v-if="errors.permissions" class="text-sm text-red-600 mt-1">{{ errors.permissions }}</p>
          </div>
          <p v-if="formError" class="text-sm text-red-600 mb-4">{{ formError }}</p>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showModal = false"
                    class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">Cancelar</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              {{ editingRole ? 'Salvar' : 'Criar perfil' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { adminUsersService } from '@/services/adminUsers'

const roles = ref([])
const permissions = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingRole = ref(null)
const formError = ref('')
const errors = ref({})
const form = reactive({
  name: '',
  code: '',
  permissions: [],
})

function slugify(s) {
  return String(s)
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
}

async function loadRoles() {
  loading.value = true
  try {
    const { data } = await adminUsersService.listRoles()
    roles.value = Array.isArray(data) ? data : (data.results || data)
  } catch (err) {
    roles.value = []
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function loadPermissions() {
  try {
    const { data } = await adminUsersService.listPermissions()
    permissions.value = Array.isArray(data) ? data : []
  } catch {
    permissions.value = []
  }
}

function openModal(role = null) {
  editingRole.value = role
  form.name = role?.name ?? ''
  form.code = role?.code ?? ''
  form.permissions = Array.isArray(role?.permissions) ? [...role.permissions] : []
  formError.value = ''
  errors.value = {}
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingRole.value = null
}

async function saveRole() {
  formError.value = ''
  errors.value = {}
  const code = (form.code || '').trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
  if (!code) {
    errors.value.code = 'Código inválido.'
    return
  }
  const payload = {
    name: form.name.trim(),
    code,
    description: '',
    permissions: form.permissions,
  }
  try {
    if (editingRole.value) {
      await adminUsersService.updateRole(editingRole.value.id, payload)
      alert('Perfil atualizado com sucesso.')
    } else {
      await adminUsersService.createRole(payload)
      alert('Perfil criado com sucesso.')
    }
    await loadRoles()
    closeModal()
  } catch (err) {
    const data = err.response?.data || {}
    Object.keys(data).forEach(k => {
      errors.value[k] = Array.isArray(data[k]) ? data[k][0] : data[k]
    })
    formError.value = data.detail || err.message || 'Erro ao salvar perfil'
  }
}

async function deleteRole(role) {
  if (!confirm(`Excluir o perfil "${role.name}"? Usuários com este perfil ficarão sem perfil customizado.`)) return
  try {
    await adminUsersService.deleteRole(role.id)
    await loadRoles()
    alert('Perfil excluído.')
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao excluir perfil')
  }
}

onMounted(async () => {
  await loadPermissions()
  await loadRoles()
})
</script>
