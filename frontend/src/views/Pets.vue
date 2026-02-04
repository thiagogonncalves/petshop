<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Animais</h1>
      </div>
      <button
        type="button"
        :disabled="!subscriptionStore.canWrite"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="openModal()"
      >
        Novo Animal
      </button>
    </div>

    <!-- Tabela de Animais -->
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Cliente</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Espécie</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Raça</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Idade</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="pet in pets" :key="pet.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <img v-if="pet.photo" 
                     :src="pet.photo" 
                     :alt="pet.name"
                     class="w-10 h-10 rounded-full object-cover mr-3 border-2 border-orange-200">
                <span class="text-sm font-medium text-gray-900">{{ pet.name }}</span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ pet.client_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ pet.species_display }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ pet.breed || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ pet.age ? `${pet.age} anos` : '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="printCard(pet.id)" class="text-orange-600 hover:text-orange-800 mr-2" title="Imprimir Carteirinha">
                <svg class="w-5 h-5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
              </button>
              <button type="button" :disabled="!subscriptionStore.canWrite" class="text-blue-600 hover:text-blue-800 mr-4 disabled:opacity-50 disabled:cursor-not-allowed" @click="openModal(pet)">Editar</button>
              <button type="button" :disabled="!subscriptionStore.canWrite" class="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed" @click="deletePet(pet.id)">Excluir</button>
            </td>
          </tr>
          <tr v-if="pets.length === 0">
            <td colspan="6" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum animal encontrado</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal de Animal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeModal">
      <div class="relative top-10 mx-auto p-6 border-2 border-orange-300 w-full max-w-2xl shadow-2xl rounded-xl bg-white max-h-[90vh] overflow-y-auto">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">{{ editingPet ? 'Editar Animal' : 'Novo Animal' }}</h3>
        </div>
        
        <form @submit.prevent="savePet">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input v-model="form.name" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
              <select v-model="form.client" required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="">Selecione...</option>
                <option v-for="client in clients" :key="client.id" :value="client.id">{{ client.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Espécie</label>
              <select v-model="form.species" required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="dog">Cão</option>
                <option value="cat">Gato</option>
                <option value="bird">Ave</option>
                <option value="fish">Peixe</option>
                <option value="reptile">Réptil</option>
                <option value="rodent">Roedor</option>
                <option value="other">Outro</option>
              </select>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Raça</label>
              <input v-model="form.breed" type="text"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Data de Nascimento</label>
              <input v-model="form.birth_date" type="date"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Peso (kg)</label>
              <input v-model="form.weight" type="number" step="0.1" min="0"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Sexo</label>
            <select v-model="form.sex"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <option value="male">Macho</option>
              <option value="female">Fêmea</option>
              <option value="unknown">Não informado</option>
            </select>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Cor</label>
            <input v-model="form.color" type="text"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Foto do Animal</label>
            <div v-if="form.photo" class="mb-2">
              <img :src="form.photo" alt="Foto do pet" class="w-32 h-32 object-cover rounded-lg border-2 border-orange-200">
            </div>
            <input 
              type="file" 
              @change="handlePhotoUpload"
              accept="image/*"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
            <p class="text-xs text-gray-500 mt-1">Formatos aceitos: JPG, PNG, GIF</p>
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
import { petsService } from '@/services/pets'
import { clientsService } from '@/services/clients'
import { useSubscriptionStore } from '@/stores/subscription'

const subscriptionStore = useSubscriptionStore()
const pets = ref([])
const clients = ref([])
const showModal = ref(false)
const editingPet = ref(null)

const form = ref({
  name: '',
  client: '',
  species: 'dog',
  breed: '',
  birth_date: '',
  weight: '',
  sex: 'unknown',
  color: '',
  is_active: true,
})

const loadPets = async () => {
  try {
    const response = await petsService.getAll()
    pets.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar animais:', error)
    alert('Erro ao carregar animais')
  }
}

const loadClients = async () => {
  try {
    const response = await clientsService.getAll({ is_active: true })
    clients.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar clientes:', error)
  }
}

const openModal = (pet = null) => {
  editingPet.value = pet
  if (pet) {
    form.value = { ...pet }
    if (form.value.birth_date) {
      form.value.birth_date = form.value.birth_date.split('T')[0]
    }
    // Photo URL is already complete from backend
  } else {
    form.value = {
      name: '',
      client: '',
      species: 'dog',
      breed: '',
      birth_date: '',
      weight: '',
      sex: 'unknown',
      color: '',
      photo: null,
      photo_file: null,
      is_active: true,
    }
  }
  showModal.value = true
}

const handlePhotoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    form.value.photo_file = file
    // Preview
    const reader = new FileReader()
    reader.onload = (e) => {
      form.value.photo = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const closeModal = () => {
  showModal.value = false
  editingPet.value = null
}

const savePet = async () => {
  try {
    const formData = new FormData()
    
    formData.append('name', form.value.name)
    formData.append('client', form.value.client)
    formData.append('species', form.value.species)
    formData.append('breed', form.value.breed || '')
    if (form.value.birth_date) formData.append('birth_date', form.value.birth_date)
    if (form.value.weight) formData.append('weight', form.value.weight)
    formData.append('sex', form.value.sex)
    formData.append('color', form.value.color || '')
    formData.append('is_active', form.value.is_active)
    if (form.value.photo_file) {
      formData.append('photo', form.value.photo_file)
    }
    
    if (editingPet.value) {
      await petsService.update(editingPet.value.id, formData)
    } else {
      await petsService.create(formData)
    }
    await loadPets()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar animal:', error)
    const errorMsg = error.response?.data?.details || error.response?.data?.error || 'Erro ao salvar animal'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

const printCard = async (petId) => {
  try {
    const response = await petsService.getCard(petId)
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `carteirinha_pet_${petId}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Erro ao gerar carteirinha:', error)
    alert('Erro ao gerar carteirinha')
  }
}

const deletePet = async (id) => {
  if (!confirm('Deseja realmente excluir este animal?')) return
  
  try {
    await petsService.delete(id)
    await loadPets()
  } catch (error) {
    console.error('Erro ao excluir animal:', error)
    alert('Erro ao excluir animal')
  }
}

onMounted(() => {
  loadPets()
  loadClients()
})
</script>