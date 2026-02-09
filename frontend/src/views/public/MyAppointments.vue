<template>
  <div class="min-h-screen bg-orange-50 p-4 pb-8">
    <div class="max-w-md mx-auto">
      <div v-if="company.name" class="text-center mb-4">
        <p class="text-lg font-semibold text-gray-800">{{ company.name }}</p>
      </div>
      <h1 class="text-2xl font-bold text-orange-800 text-center mb-6">Meus Agendamentos</h1>

      <div class="bg-white rounded-xl shadow-lg p-6 mb-4">
        <p class="text-gray-600 mb-2">Informe seu CPF para ver seus agendamentos</p>
        <input
          v-model="cpf"
          type="text"
          placeholder="000.000.000-00"
          maxlength="14"
          class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl mb-3"
          @input="maskCpf"
        />
        <button
          @click="loadAppointments"
          :disabled="loading || cpf.replace(/\D/g,'').length !== 11"
          class="w-full py-3 bg-orange-500 text-white font-bold rounded-xl disabled:opacity-50"
        >
          {{ loading ? 'Carregando...' : 'Buscar' }}
        </button>
      </div>

      <div v-if="appointments.length > 0" class="space-y-3">
        <div v-for="apt in appointments" :key="apt.id"
             class="bg-white rounded-xl shadow p-4 border-l-4"
             :class="getStatusBorderClass(apt.status)">
          <p class="font-semibold text-gray-800">{{ apt.service_name }}</p>
          <p class="text-sm text-gray-600">{{ apt.pet_name }} • {{ apt.client_name }}</p>
          <p class="text-sm font-medium text-orange-600">{{ formatDateTime(apt.start_at || apt.scheduled_date) }}</p>
          <span :class="getStatusClass(apt.status)" class="inline-block mt-2 px-2 py-0.5 rounded text-xs font-medium">
            {{ apt.status_display }}
          </span>
        </div>
      </div>
      <div v-else-if="searched && !loading" class="bg-white rounded-xl shadow p-6 text-center text-gray-500">
        Nenhum agendamento encontrado para este CPF.
      </div>

      <router-link to="/agendar" class="block mt-6 text-center text-orange-600 font-medium">
        ← Fazer novo agendamento
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bookingService } from '@/services/booking'
import { companyService } from '@/services/company'

const company = ref({})
const cpf = ref('')
const appointments = ref([])
const loading = ref(false)
const searched = ref(false)

function maskCpf() {
  const digits = cpf.value.replace(/\D/g, '').slice(0, 11)
  cpf.value = digits.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4').replace(/(\d{3})(\d{3})(\d)/, '$1.$2.$3')
}

async function loadAppointments() {
  const digits = cpf.value.replace(/\D/g, '')
  if (digits.length !== 11) return
  loading.value = true
  searched.value = true
  try {
    const res = await bookingService.getMyAppointments(digits)
    appointments.value = res.data
  } catch {
    appointments.value = []
  } finally {
    loading.value = false
  }
}

function formatDateTime(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function getStatusClass(status) {
  const map = {
    scheduled: 'bg-blue-100 text-blue-800',
    confirmed: 'bg-green-100 text-green-800',
    done: 'bg-gray-100 text-gray-800',
    cancelled: 'bg-red-100 text-red-800',
    no_show: 'bg-gray-100 text-gray-800',
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

function getStatusBorderClass(status) {
  const map = {
    scheduled: 'border-blue-500',
    confirmed: 'border-green-500',
    done: 'border-gray-400',
    cancelled: 'border-red-400',
  }
  return map[status] || 'border-gray-300'
}

onMounted(async () => {
  try {
    const { data } = await companyService.get()
    company.value = data || {}
    document.title = (data?.name || 'Sistema de Gestão para Pet Shop') + ' - Meus Agendamentos'
  } catch {
    company.value = {}
  }
})
</script>
