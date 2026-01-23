<template>
  <div>
    <div class="flex items-center mb-6">
      <svg class="w-8 h-8 text-blue-600 mr-3" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
      <h1 class="text-3xl font-bold text-blue-800">Dashboard</h1>
    </div>
    
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <div class="bg-white overflow-hidden shadow-lg rounded-lg border-2 border-orange-200 hover:shadow-xl transition-all hover:border-orange-300">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="bg-gradient-to-br from-orange-100 to-blue-100 rounded-lg p-3">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-600 truncate">Vendas Hoje</dt>
                <dd class="text-2xl font-bold text-gray-900">{{ dashboard.sales?.today?.count || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white overflow-hidden shadow-lg rounded-lg border-2 border-orange-200 hover:shadow-xl transition-all hover:border-orange-300">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="bg-gradient-to-br from-orange-100 to-blue-100 rounded-lg p-3">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-600 truncate">Agendamentos Hoje</dt>
                <dd class="text-2xl font-bold text-gray-900">{{ dashboard.appointments?.today || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white overflow-hidden shadow-lg rounded-lg border-2 border-orange-200 hover:shadow-xl transition-all hover:border-orange-300">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="bg-gradient-to-br from-orange-100 to-blue-100 rounded-lg p-3">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-600 truncate">Total Clientes</dt>
                <dd class="text-2xl font-bold text-gray-900">{{ dashboard.clients?.total || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white overflow-hidden shadow-lg rounded-lg border-2 border-orange-200 hover:shadow-xl transition-all hover:border-orange-300">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="bg-gradient-to-br from-orange-100 to-blue-100 rounded-lg p-3">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-600 truncate">Estoque Baixo</dt>
                <dd class="text-2xl font-bold text-gray-900">{{ dashboard.inventory?.low_stock_count || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Lista de Agendamentos do Dia -->
    <div class="bg-white shadow-lg rounded-lg border-2 border-orange-200 overflow-hidden mt-8">
      <div class="bg-gradient-to-r from-orange-400 to-orange-300 px-6 py-4 border-b-2 border-orange-500">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-6 h-6 text-white mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h2 class="text-xl font-bold text-white">Agendamentos de Hoje</h2>
          </div>
          <span class="bg-white text-orange-600 px-3 py-1 rounded-full text-sm font-semibold">
            {{ todayAppointments.length }} agendamento(s)
          </span>
        </div>
      </div>
      
      <div v-if="loadingAppointments" class="p-6 text-center">
        <div class="text-gray-500">Carregando agendamentos...</div>
      </div>
      
      <div v-else-if="todayAppointments.length === 0" class="p-6 text-center">
        <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="text-gray-500 text-lg">Nenhum agendamento para hoje</p>
      </div>
      
      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="appointment in todayAppointments"
          :key="appointment.id"
          class="p-6 hover:bg-orange-50 transition-colors"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-2">
                <div class="flex-shrink-0 mr-4">
                  <div :class="[
                    'w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg',
                    appointment.status === 'in_progress' ? 'bg-blue-500' :
                    appointment.status === 'scheduled' ? 'bg-green-500' :
                    'bg-gray-400'
                  ]">
                    {{ formatTime(appointment.scheduled_date) }}
                  </div>
                </div>
                <div class="flex-1">
                  <div class="flex items-center mb-1">
                    <h3 class="text-lg font-semibold text-gray-900">{{ appointment.pet_name }}</h3>
                    <span :class="[
                      'ml-3 px-2 py-1 rounded-full text-xs font-medium',
                      appointment.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      appointment.status === 'scheduled' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    ]">
                      {{ appointment.status_display }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 mb-1">
                    <span class="font-medium">Cliente:</span> {{ appointment.client_name }}
                  </p>
                  <p class="text-sm text-gray-600 mb-1">
                    <span class="font-medium">Serviço:</span> {{ appointment.service_name }}
                    <span class="text-gray-500 ml-2">• R$ {{ formatPrice(appointment.service_price) }}</span>
                  </p>
                  <p v-if="appointment.observations" class="text-sm text-gray-500 mt-2 italic">
                    {{ appointment.observations }}
                  </p>
                </div>
              </div>
            </div>
            <div class="ml-4 flex space-x-2">
              <button
                v-if="appointment.status === 'scheduled'"
                @click="completeAppointment(appointment.id)"
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium transition-colors"
              >
                Concluir
              </button>
              <button
                v-if="appointment.status !== 'cancelled' && appointment.status !== 'completed'"
                @click="cancelAppointment(appointment.id)"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { schedulingService } from '@/services/scheduling'

const dashboard = ref({})
const todayAppointments = ref([])
const loadingAppointments = ref(false)

const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

const formatPrice = (price) => {
  return parseFloat(price).toFixed(2).replace('.', ',')
}

const loadTodayAppointments = async () => {
  loadingAppointments.value = true
  try {
    const response = await schedulingService.getToday()
    todayAppointments.value = response.data
  } catch (error) {
    console.error('Erro ao carregar agendamentos:', error)
  } finally {
    loadingAppointments.value = false
  }
}

const completeAppointment = async (id) => {
  if (!confirm('Deseja marcar este agendamento como concluído?')) return
  
  try {
    await schedulingService.complete(id)
    await loadTodayAppointments()
    await loadDashboard()
  } catch (error) {
    console.error('Erro ao concluir agendamento:', error)
    alert('Erro ao concluir agendamento')
  }
}

const cancelAppointment = async (id) => {
  if (!confirm('Deseja cancelar este agendamento?')) return
  
  try {
    await schedulingService.cancel(id)
    await loadTodayAppointments()
    await loadDashboard()
  } catch (error) {
    console.error('Erro ao cancelar agendamento:', error)
    alert('Erro ao cancelar agendamento')
  }
}

const loadDashboard = async () => {
  try {
    const response = await api.get('/reports/dashboard/')
    dashboard.value = response.data
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error)
  }
}

onMounted(async () => {
  await loadDashboard()
  await loadTodayAppointments()
})
</script>
