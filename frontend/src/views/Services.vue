<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Serviços</h1>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors"
      >
        Novo Serviço
      </button>
    </div>

    <!-- Tabela de Serviços -->
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Valor</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Duração</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="service in services" :key="service.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ service.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">R$ {{ formatPrice(service.price) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ service.duration_minutes }} min</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="service.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" 
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ service.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="openModal(service)" class="text-blue-600 hover:text-blue-800 mr-4">Editar</button>
              <button @click="deleteService(service.id)" class="text-red-600 hover:text-red-900">Excluir</button>
            </td>
          </tr>
          <tr v-if="services.length === 0">
            <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum serviço encontrado</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal de Serviço -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeModal">
      <div class="relative top-10 mx-auto p-6 border-2 border-orange-300 w-full max-w-2xl shadow-2xl rounded-xl bg-white">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">{{ editingService ? 'Editar Serviço' : 'Novo Serviço' }}</h3>
        </div>
        
        <form @submit.prevent="saveService">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input v-model="form.name" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
              <textarea v-model="form.description" rows="3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Valor</label>
              <input v-model="form.price" type="number" step="0.01" min="0.01" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Duração (min)</label>
              <input v-model="form.duration_minutes" type="number" min="1" required
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
import { servicesService } from '@/services/services'

const services = ref([])
const showModal = ref(false)
const editingService = ref(null)

const form = ref({
  name: '',
  description: '',
  price: 0,
  duration_minutes: 30,
  is_active: true,
})

const loadServices = async () => {
  try {
    const response = await servicesService.getAll()
    services.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar serviços:', error)
    alert('Erro ao carregar serviços')
  }
}

const openModal = (service = null) => {
  editingService.value = service
  if (service) {
    form.value = { ...service }
  } else {
    form.value = {
      name: '',
      description: '',
      price: 0,
      duration_minutes: 30,
      is_active: true,
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingService.value = null
}

const saveService = async () => {
  try {
    const data = {
      ...form.value,
      price: parseFloat(form.value.price),
      duration_minutes: parseInt(form.value.duration_minutes),
    }
    
    if (editingService.value) {
      await servicesService.update(editingService.value.id, data)
    } else {
      await servicesService.create(data)
    }
    await loadServices()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar serviço:', error)
    const errorMsg = error.response?.data?.details || error.response?.data?.error || 'Erro ao salvar serviço'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

const deleteService = async (id) => {
  if (!confirm('Deseja realmente excluir este serviço?')) return
  
  try {
    await servicesService.delete(id)
    await loadServices()
  } catch (error) {
    console.error('Erro ao excluir serviço:', error)
    alert('Erro ao excluir serviço')
  }
}

const formatPrice = (price) => {
  return parseFloat(price).toFixed(2).replace('.', ',')
}

onMounted(() => {
  loadServices()
})
</script>