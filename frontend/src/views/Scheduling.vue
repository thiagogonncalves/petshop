<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Agendamentos</h1>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors"
      >
        Novo Agendamento
      </button>
    </div>

    <!-- Tabela de Agendamentos -->
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Data/Hora</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Cliente</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Animal</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Serviço</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="appointment in appointments" :key="appointment.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatDateTime(appointment.start_at || appointment.scheduled_date) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ appointment.client_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ appointment.pet_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ appointment.service_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusColor(appointment.status)" 
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ appointment.status_display }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button v-if="appointment.status === 'scheduled'" @click="completeAppointment(appointment.id)" 
                      class="text-green-600 hover:text-green-900 mr-4">Concluir</button>
              <button v-if="appointment.status === 'scheduled'" @click="cancelAppointment(appointment.id)" 
                      class="text-red-600 hover:text-red-900 mr-4">Cancelar</button>
              <button @click="openModal(appointment)" class="text-blue-600 hover:text-blue-800">Editar</button>
            </td>
          </tr>
          <tr v-if="appointments.length === 0">
            <td colspan="6" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum agendamento encontrado</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal de Agendamento -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeModal">
      <div class="relative top-10 mx-auto p-6 border-2 border-orange-300 w-full max-w-2xl shadow-2xl rounded-xl bg-white">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">{{ editingAppointment ? 'Editar Agendamento' : 'Novo Agendamento' }}</h3>
        </div>
        
        <form @submit.prevent="saveAppointment">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
              <select v-model="form.client" required @change="loadClientPets"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="">Selecione...</option>
                <option v-for="client in clients" :key="client.id" :value="client.id">{{ client.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Animal</label>
              <select v-model="form.pet" required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="">Selecione...</option>
                <option v-for="pet in clientPets" :key="pet.id" :value="pet.id">{{ pet.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Serviço</label>
              <select v-model="form.service" required @change="onServiceChange"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="">Selecione...</option>
                <option v-for="service in services" :key="service.id" :value="service.id">{{ service.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Data</label>
              <input v-model="formDate" type="date" :min="minDate"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                     @change="onDateChange">
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Horário</label>
              <button v-if="form.service && formDate" type="button"
                      @click="loadSlots(editingAppointment?.id)"
                      class="mb-3 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 text-sm">
                {{ loadingSlots ? 'Carregando...' : 'Ver horários disponíveis' }}
              </button>
              <div v-if="loadingSlots" class="text-sm text-gray-500 py-2">Carregando horários...</div>
              <div v-else-if="slots.length === 0 && form.service && formDate && slotsLoaded" 
                   class="text-amber-700 bg-amber-50 p-4 rounded-xl text-sm">
                Nenhum horário disponível nesta data. Escolha outra data.
              </div>
              <div v-else-if="slots.length > 0" class="grid grid-cols-3 gap-2">
                <button v-for="slot in slots" :key="slot" type="button"
                        @click="selectSlot(slot)"
                        class="py-3 rounded-xl font-medium transition-colors"
                        :class="formTime === slot ? 'bg-orange-500 text-white' : 'bg-gray-100 text-gray-800 hover:bg-orange-100'">
                  {{ slot }}
                </button>
              </div>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Observações</label>
              <textarea v-model="form.observations" rows="3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
            </div>
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
import { ref, computed, onMounted } from 'vue'
import { schedulingService } from '@/services/scheduling'
import { clientsService } from '@/services/clients'
import { petsService } from '@/services/pets'
import { servicesService } from '@/services/services'
import { bookingService } from '@/services/booking'

const appointments = ref([])
const clients = ref([])
const services = ref([])
const clientPets = ref([])
const showModal = ref(false)
const editingAppointment = ref(null)

const form = ref({
  client: '',
  pet: '',
  service: '',
  scheduled_date: '',
  observations: '',
  status: 'scheduled',
})

const formDate = ref('')
const formTime = ref('')
const slots = ref([])
const loadingSlots = ref(false)
const slotsLoaded = ref(false)

const minDate = computed(() => new Date().toISOString().slice(0, 10))

const loadAppointments = async () => {
  try {
    const response = await schedulingService.getAll()
    appointments.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar agendamentos:', error)
    alert('Erro ao carregar agendamentos')
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

const loadServices = async () => {
  try {
    const response = await servicesService.getAll({ is_active: true })
    services.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar serviços:', error)
  }
}

const loadClientPets = async () => {
  if (!form.value.client) {
    clientPets.value = []
    return
  }
  
  try {
    const response = await clientsService.getPets(form.value.client)
    clientPets.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar animais do cliente:', error)
    clientPets.value = []
  }
}

function onDateChange() {
  formTime.value = ''
  slots.value = []
  slotsLoaded.value = false
}

function onServiceChange() {
  formTime.value = ''
  slots.value = []
  slotsLoaded.value = false
}

async function loadSlots(excludeAppointmentId = null) {
  if (!form.value.service || !formDate.value) return
  loadingSlots.value = true
  slots.value = []
  slotsLoaded.value = false
  try {
    const res = await bookingService.getAvailableSlots(
      form.value.service, formDate.value, excludeAppointmentId
    )
    slots.value = res.data.slots || []
  } catch {
    slots.value = []
  } finally {
    loadingSlots.value = false
    slotsLoaded.value = true
  }
}

function selectSlot(slot) {
  formTime.value = slot
  form.value.scheduled_date = `${formDate.value}T${slot}:00`
}

const openModal = async (appointment = null) => {
  editingAppointment.value = appointment
  formDate.value = ''
  formTime.value = ''
  slots.value = []
  slotsLoaded.value = false
  if (appointment) {
    form.value = { ...appointment }
    const dt = form.value.start_at || form.value.scheduled_date
    if (dt) {
      const date = new Date(dt)
      formDate.value = date.toISOString().slice(0, 10)
      formTime.value = date.toTimeString().slice(0, 5)
      form.value.scheduled_date = date.toISOString().slice(0, 16)
      if (form.value.service && formDate.value) {
        await loadSlots(editingAppointment.value?.id)
      }
    }
    if (form.value.client) {
      loadClientPets()
    }
  } else {
    form.value = {
      client: '',
      pet: '',
      service: '',
      scheduled_date: '',
      observations: '',
      status: 'scheduled',
    }
    clientPets.value = []
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingAppointment.value = null
}

const saveAppointment = async () => {
  if (!formTime.value && form.value.service && formDate.value) {
    alert('Clique em "Ver horários disponíveis" e selecione um horário.')
    return
  }
  if (form.value.service && formDate.value && !formTime.value) {
    alert('Selecione um horário disponível.')
    return
  }
  try {
    const data = {
      ...form.value,
      client: parseInt(form.value.client),
      pet: parseInt(form.value.pet),
      service: parseInt(form.value.service),
      scheduled_date: form.value.scheduled_date || (formDate.value && formTime.value ? `${formDate.value}T${formTime.value}:00` : ''),
    }
    
    if (editingAppointment.value) {
      await schedulingService.update(editingAppointment.value.id, data)
    } else {
      await schedulingService.create(data)
    }
    await loadAppointments()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar agendamento:', error)
    const data = error.response?.data || {}
    let errorMsg = data.detail || data.details || data.error
    if (!errorMsg && typeof data === 'object') {
      const firstKey = Object.keys(data)[0]
      const val = firstKey ? data[firstKey] : null
      errorMsg = Array.isArray(val) ? val[0] : (val || 'Erro ao salvar agendamento')
    }
    alert(typeof errorMsg === 'string' ? errorMsg : (errorMsg ? JSON.stringify(errorMsg) : 'Erro ao salvar agendamento'))
  }
}

const completeAppointment = async (id) => {
  try {
    await schedulingService.complete(id)
    await loadAppointments()
  } catch (error) {
    console.error('Erro ao completar agendamento:', error)
    alert('Erro ao completar agendamento')
  }
}

const cancelAppointment = async (id) => {
  if (!confirm('Deseja realmente cancelar este agendamento?')) return
  
  try {
    await schedulingService.cancel(id)
    await loadAppointments()
  } catch (error) {
    console.error('Erro ao cancelar agendamento:', error)
    alert('Erro ao cancelar agendamento')
  }
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR')
}

const getStatusColor = (status) => {
  const colors = {
    'scheduled': 'bg-blue-100 text-blue-800',
    'in_progress': 'bg-yellow-100 text-yellow-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800',
    'no_show': 'bg-gray-100 text-gray-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  loadAppointments()
  loadClients()
  loadServices()
})
</script>