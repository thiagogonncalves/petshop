<template>
  <div class="min-h-screen bg-orange-50 p-4 pb-8">
    <div class="max-w-md mx-auto">
      <h1 class="text-2xl font-bold text-orange-800 text-center mb-6">Agendar Serviço</h1>

      <!-- Step 1: CPF -->
      <div v-if="step === 1" class="bg-white rounded-xl shadow-lg p-6">
        <p class="text-gray-600 mb-4">Informe seu CPF para continuar</p>
        <input
          v-model="cpf"
          type="text"
          placeholder="000.000.000-00"
          maxlength="14"
          class="w-full px-4 py-4 text-lg border-2 border-gray-300 rounded-xl mb-4"
          @input="maskCpf"
        />
        <p v-if="cpfError" class="text-red-600 text-sm mb-2">{{ cpfError }}</p>
        <button
          @click="checkCpf"
          :disabled="checking || cpf.replace(/\D/g,'').length !== 11"
          class="w-full py-4 bg-orange-500 text-white font-bold rounded-xl disabled:opacity-50"
        >
          {{ checking ? 'Verificando...' : 'Continuar' }}
        </button>
      </div>

      <!-- Step 2a: Novo cliente - cadastro -->
      <div v-else-if="step === 2 && !clientExists" class="bg-white rounded-xl shadow-lg p-6 space-y-4">
        <p class="text-gray-600">Cadastre-se para agendar</p>
        <input v-model="newClient.name" type="text" placeholder="Nome completo" required
               class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl" />
        <input v-model="newClient.phone" type="tel" placeholder="Telefone" required
               class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl" />
        <input v-model="newPet.name" type="text" placeholder="Nome do pet" required
               class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl" />
        <select v-model="newPet.species" class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl">
          <option value="dog">Cão</option>
          <option value="cat">Gato</option>
          <option value="bird">Ave</option>
          <option value="other">Outro</option>
        </select>
        <p v-if="registerError" class="text-red-600 text-sm">{{ registerError }}</p>
        <button @click="register" :disabled="registering"
                class="w-full py-4 bg-orange-500 text-white font-bold rounded-xl disabled:opacity-50">
          {{ registering ? 'Cadastrando...' : 'Cadastrar e continuar' }}
        </button>
      </div>

      <!-- Step 2b: Cliente existente - selecionar pet -->
      <div v-else-if="step === 2 && clientExists" class="bg-white rounded-xl shadow-lg p-6 space-y-4">
        <p class="text-gray-600">Olá, <strong>{{ client?.name }}</strong>!</p>
        <p class="text-sm text-gray-500">Selecione o pet:</p>
        <select v-model="selectedPetId" class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl">
          <option value="">Selecione...</option>
          <option v-for="p in pets" :key="p.id" :value="p.id">{{ p.name }} ({{ p.species_display || p.species }})</option>
        </select>
        <p v-if="petError" class="text-red-600 text-sm">{{ petError }}</p>
        <button @click="goToService" :disabled="!selectedPetId"
                class="w-full py-4 bg-orange-500 text-white font-bold rounded-xl disabled:opacity-50">
          Continuar
        </button>
      </div>

      <!-- Step 3: Serviço -->
      <div v-else-if="step === 3" class="bg-white rounded-xl shadow-lg p-6 space-y-4">
        <p class="text-gray-600">Selecione o serviço</p>
        <div v-for="s in services" :key="s.id"
             class="p-4 border-2 rounded-xl cursor-pointer transition-colors"
             :class="selectedServiceId === s.id ? 'border-orange-500 bg-orange-50' : 'border-gray-200'"
             @click="selectedServiceId = s.id">
          <p class="font-semibold text-gray-800">{{ s.name }}</p>
          <p class="text-sm text-gray-600">R$ {{ formatPrice(s.price) }} • {{ s.duration_minutes }} min</p>
        </div>
        <button @click="goToDate" :disabled="!selectedServiceId"
                class="w-full py-4 bg-orange-500 text-white font-bold rounded-xl disabled:opacity-50">
          Continuar
        </button>
      </div>

      <!-- Step 4: Data -->
      <div v-else-if="step === 4" class="bg-white rounded-xl shadow-lg p-6 space-y-4">
        <p class="text-gray-600">Escolha a data</p>
        <input v-model="selectedDate" type="date" :min="minDate"
               class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl text-lg" />
        <p v-if="dateError" class="text-red-600 text-sm">{{ dateError }}</p>
        <button @click="loadSlots" :disabled="!selectedDate"
                class="w-full py-4 bg-orange-500 text-white font-bold rounded-xl disabled:opacity-50">
          Ver horários disponíveis
        </button>
      </div>

      <!-- Step 5: Horário -->
      <div v-else-if="step === 5" class="bg-white rounded-xl shadow-lg p-6 space-y-4">
        <p class="text-gray-600">Horários disponíveis para {{ formatDateBr(selectedDate) }}</p>
        <div v-if="loadingSlots" class="text-center py-8 text-gray-500">Carregando...</div>
        <div v-else-if="slots.length === 0" class="text-amber-700 bg-amber-50 p-4 rounded-xl">
          Nenhum horário disponível nesta data. Escolha outra data.
        </div>
        <div v-else class="grid grid-cols-3 gap-2">
          <button v-for="slot in slots" :key="slot"
                  @click="selectedTime = slot"
                  class="py-3 rounded-xl font-medium transition-colors"
                  :class="selectedTime === slot ? 'bg-orange-500 text-white' : 'bg-gray-100 text-gray-800 hover:bg-orange-100'">
            {{ slot }}
          </button>
        </div>
        <button @click="goToConfirm" :disabled="!selectedTime"
                class="w-full py-4 bg-orange-500 text-white font-bold rounded-xl disabled:opacity-50 mt-4">
          Continuar
        </button>
      </div>

      <!-- Step 6: Confirmar -->
      <div v-else-if="step === 6" class="bg-white rounded-xl shadow-lg p-6 space-y-4">
        <p class="text-gray-600 font-semibold">Confirme seu agendamento</p>
        <div class="bg-gray-50 p-4 rounded-xl space-y-2">
          <p><strong>Cliente:</strong> {{ client?.name }}</p>
          <p><strong>Pet:</strong> {{ selectedPetName }}</p>
          <p><strong>Serviço:</strong> {{ selectedServiceName }}</p>
          <p><strong>Data:</strong> {{ formatDateBr(selectedDate) }}</p>
          <p><strong>Horário:</strong> {{ selectedTime }}</p>
        </div>
        <textarea v-model="notes" placeholder="Observações (opcional)" rows="2"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl"></textarea>
        <p v-if="bookError" class="text-red-600 text-sm">{{ bookError }}</p>
        <button @click="confirmBooking" :disabled="booking"
                class="w-full py-4 bg-green-600 text-white font-bold rounded-xl disabled:opacity-50">
          {{ booking ? 'Agendando...' : 'Confirmar agendamento' }}
        </button>
      </div>

      <!-- Sucesso -->
      <div v-else-if="step === 7" class="bg-white rounded-xl shadow-lg p-8 text-center">
        <div class="text-6xl mb-4">✅</div>
        <h2 class="text-xl font-bold text-green-800 mb-2">Agendamento realizado!</h2>
        <p class="text-gray-600 mb-4">{{ formatDateBr(selectedDate) }} às {{ selectedTime }}</p>
        <p class="text-sm text-gray-500 mb-6">{{ selectedServiceName }}</p>
        <button type="button" @click="resetWizard"
                class="block w-full py-4 bg-orange-500 text-white font-bold rounded-xl hover:bg-orange-600">
          Fazer novo agendamento
        </button>
        <router-link to="/agendar/meus" class="block w-full py-3 text-orange-600 font-medium mt-2">
          Meus agendamentos
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { bookingService } from '@/services/booking'

const router = useRouter()
const step = ref(1)
const cpf = ref('')
const cpfError = ref('')
const checking = ref(false)
const clientExists = ref(false)
const client = ref(null)
const pets = ref([])
const selectedPetId = ref('')
const petError = ref('')
const newClient = ref({ name: '', phone: '' })
const newPet = ref({ name: '', species: 'dog' })
const registerError = ref('')
const registering = ref(false)
const services = ref([])
const selectedServiceId = ref('')
const selectedDate = ref('')
const dateError = ref('')
const slots = ref([])
const loadingSlots = ref(false)
const selectedTime = ref('')
const notes = ref('')
const bookError = ref('')
const booking = ref(false)

const minDate = computed(() => new Date().toISOString().slice(0, 10))

const selectedPetName = computed(() => {
  const p = pets.value.find(x => x.id === parseInt(selectedPetId.value))
  return p?.name || ''
})
const selectedServiceName = computed(() => {
  const s = services.value.find(x => x.id === parseInt(selectedServiceId.value))
  return s?.name || ''
})

function maskCpf() {
  const digits = cpf.value.replace(/\D/g, '').slice(0, 11)
  cpf.value = digits.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4').replace(/(\d{3})(\d{3})(\d)/, '$1.$2.$3')
  cpfError.value = ''
}

async function checkCpf() {
  const digits = cpf.value.replace(/\D/g, '')
  if (digits.length !== 11) {
    cpfError.value = 'CPF deve ter 11 dígitos'
    return
  }
  checking.value = true
  cpfError.value = ''
  try {
    const res = await bookingService.checkCpf(digits)
    clientExists.value = res.data.exists
    client.value = res.data.client || null
    if (clientExists.value && client.value) {
      pets.value = res.data.pets || []
      selectedPetId.value = pets.value[0] ? String(pets.value[0].id) : ''
    }
    step.value = 2
  } catch (e) {
    cpfError.value = e.response?.data?.detail || 'Erro ao verificar CPF'
  } finally {
    checking.value = false
  }
}

async function register() {
  if (!newClient.value.name?.trim() || !newClient.value.phone?.trim() || !newPet.value.name?.trim()) {
    registerError.value = 'Preencha todos os campos obrigatórios'
    return
  }
  registering.value = true
  registerError.value = ''
  try {
    const res = await bookingService.register({
      client: {
        cpf: cpf.value.replace(/\D/g, ''),
        name: newClient.value.name.trim(),
        phone: newClient.value.phone.trim(),
      },
      pet: {
        name: newPet.value.name.trim(),
        species: newPet.value.species || 'dog',
      },
    })
    client.value = { id: res.data.client_id, name: newClient.value.name }
    selectedPetId.value = String(res.data.pet_id)
    pets.value = [{ id: res.data.pet_id, name: newPet.value.name, species_display: 'Cão' }]
    await loadServices()
    step.value = 3
  } catch (e) {
    registerError.value = e.response?.data?.detail || 'Erro ao cadastrar'
  } finally {
    registering.value = false
  }
}

async function loadServices() {
  try {
    const res = await bookingService.getServices()
    services.value = res.data
  } catch {
    services.value = []
  }
}

async function goToService() {
  if (!selectedPetId.value) {
    petError.value = 'Selecione um pet'
    return
  }
  petError.value = ''
  await loadServices()
  step.value = 3
}

function goToDate() {
  if (!selectedServiceId.value) return
  step.value = 4
  selectedDate.value = ''
  dateError.value = ''
}

async function loadSlots() {
  if (!selectedDate.value) {
    dateError.value = 'Selecione uma data'
    return
  }
  loadingSlots.value = true
  slots.value = []
  try {
    const res = await bookingService.getAvailableSlots(selectedServiceId.value, selectedDate.value)
    slots.value = res.data.slots || []
  } catch {
    slots.value = []
  } finally {
    loadingSlots.value = false
  }
  step.value = 5
  selectedTime.value = ''
}

function goToConfirm() {
  if (!selectedTime.value) return
  step.value = 6
  bookError.value = ''
}

async function confirmBooking() {
  booking.value = true
  bookError.value = ''
  try {
    await bookingService.createAppointment({
      client_id: client.value.id,
      pet_id: parseInt(selectedPetId.value),
      service_id: parseInt(selectedServiceId.value),
      date: selectedDate.value,
      time: selectedTime.value,
      notes: notes.value.trim(),
    })
    step.value = 7
  } catch (e) {
    const detail = e.response?.data?.detail
    bookError.value = (typeof detail === 'string' ? detail : JSON.stringify(detail || {})) || 'Erro ao agendar'
  } finally {
    booking.value = false
  }
}

function resetWizard() {
  step.value = 1
  cpf.value = ''
  cpfError.value = ''
  clientExists.value = false
  client.value = null
  pets.value = []
  selectedPetId.value = ''
  newClient.value = { name: '', phone: '' }
  newPet.value = { name: '', species: 'dog' }
  services.value = []
  selectedServiceId.value = ''
  selectedDate.value = ''
  slots.value = []
  selectedTime.value = ''
  notes.value = ''
  bookError.value = ''
}

function formatPrice(v) {
  if (v == null || isNaN(v)) return '0,00'
  return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDateBr(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })
}
</script>
