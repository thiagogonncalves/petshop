<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Clientes</h1>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors"
      >
        Novo Cliente
      </button>
    </div>

    <!-- Tabela de Clientes -->
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">CPF/CNPJ</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Telefone</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">E-mail</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="client in clients" :key="client.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ client.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ client.document }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ client.phone }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ client.email || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="client.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" 
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ client.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <router-link :to="{ name: 'ClientCredits', params: { clientId: client.id } }" class="text-orange-600 hover:text-orange-800 mr-4">
                Crediário
              </router-link>
              <button @click="openModal(client)" class="text-blue-600 hover:text-blue-800 mr-4">Editar</button>
              <button @click="deleteClient(client.id)" class="text-red-600 hover:text-red-900">Excluir</button>
            </td>
          </tr>
          <tr v-if="clients.length === 0">
            <td colspan="6" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum cliente encontrado</td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination -->
      <Pagination
        v-if="pagination"
        :current-page="pagination.current_page || 1"
        :total-pages="pagination.total_pages || 1"
        :total-items="pagination.total_items || 0"
        :items-per-page="pagination.items_per_page || 20"
        @page-change="handlePageChange"
      />
    </div>

    <!-- Modal de Cliente -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeModal">
      <div class="relative top-10 mx-auto p-6 border-2 border-orange-300 w-full max-w-3xl shadow-2xl rounded-xl bg-white max-h-[90vh] overflow-y-auto">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">{{ editingClient ? 'Editar Cliente' : 'Novo Cliente' }}</h3>
        </div>
        
        <form @submit.prevent="saveClient">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input v-model="form.name" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Documento</label>
              <select v-model="form.document_type" required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="cpf">CPF</option>
                <option value="cnpj">CNPJ</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">CPF/CNPJ</label>
              <input v-model="form.document" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
              <input v-model="form.phone" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
              <input v-model="form.email" type="email"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Rua</label>
              <input v-model="form.street" type="text"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Número</label>
              <input v-model="form.number" type="text"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">CEP</label>
              <input v-model="form.zip_code" type="text"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Bairro</label>
              <input v-model="form.neighborhood" type="text"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Cidade</label>
              <input v-model="form.city" type="text"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
              <input v-model="form.state" type="text" maxlength="2"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
          </div>

          <div class="mb-4">
            <label class="flex items-center">
              <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
              <span class="ml-2 text-sm text-gray-700">Ativo</span>
            </label>
          </div>

          <div class="flex justify-end space-x-3">
            <button type="button" @click="closeModal" 
                    class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" 
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors">
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { clientsService } from '@/services/clients'
import Pagination from '@/components/Pagination.vue'

const clients = ref([])
const showModal = ref(false)
const editingClient = ref(null)
const pagination = ref(null)
const currentPage = ref(1)

const form = ref({
  name: '',
  document_type: 'cpf',
  document: '',
  phone: '',
  email: '',
  street: '',
  number: '',
  complement: '',
  neighborhood: '',
  city: '',
  state: '',
  zip_code: '',
  is_active: true,
})

const loadClients = async (page = 1) => {
  try {
    const response = await clientsService.getAll({ page })
    clients.value = response.data.results || response.data
    
    // Extract pagination info
    if (response.data.count !== undefined) {
      pagination.value = {
        current_page: page,
        total_pages: Math.ceil((response.data.count || 0) / (response.data.page_size || 20)),
        total_items: response.data.count || 0,
        items_per_page: response.data.page_size || 20
      }
    } else {
      pagination.value = null
    }
  } catch (error) {
    console.error('Erro ao carregar clientes:', error)
    alert('Erro ao carregar clientes')
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadClients(page)
}

const openModal = (client = null) => {
  editingClient.value = client
  if (client) {
    form.value = { ...client }
  } else {
    form.value = {
      name: '',
      document_type: 'cpf',
      document: '',
      phone: '',
      email: '',
      street: '',
      number: '',
      complement: '',
      neighborhood: '',
      city: '',
      state: '',
      zip_code: '',
      is_active: true,
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingClient.value = null
}

const saveClient = async () => {
  try {
    if (editingClient.value) {
      await clientsService.update(editingClient.value.id, form.value)
    } else {
      await clientsService.create(form.value)
    }
    await loadClients()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar cliente:', error)
    const errorMsg = error.response?.data?.details || error.response?.data?.error || 'Erro ao salvar cliente'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

const deleteClient = async (id) => {
  if (!confirm('Deseja realmente excluir este cliente?')) return
  
  try {
    await clientsService.delete(id)
    await loadClients()
  } catch (error) {
    console.error('Erro ao excluir cliente:', error)
    alert('Erro ao excluir cliente')
  }
}

onMounted(() => {
  loadClients(1)
})
</script>