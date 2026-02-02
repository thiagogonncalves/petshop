<template>
  <div>
    <div class="flex items-center mb-6">
      <svg class="w-7 h-7 text-orange-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>
      <h1 class="text-2xl font-bold text-gray-800">Crediário da Casa</h1>
    </div>

    <!-- Filtros -->
    <div class="bg-white rounded-lg shadow border border-gray-200 p-4 mb-4">
      <div class="flex flex-wrap gap-3">
        <select v-model="filters.status" class="px-3 py-2 border border-gray-300 rounded-lg text-sm" @change="loadCredits">
          <option value="">Todos os status</option>
          <option value="open">Em aberto</option>
          <option value="settled">Quitados</option>
          <option value="cancelled">Cancelados</option>
        </select>
        <input
          v-model="filters.q"
          type="text"
          placeholder="Buscar cliente..."
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm flex-1 min-w-[200px]"
          @keyup.enter="loadCredits"
        />
        <input
          v-model="filters.start"
          type="date"
          placeholder="Início"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          @change="loadCredits"
        />
        <input
          v-model="filters.end"
          type="date"
          placeholder="Fim"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          @change="loadCredits"
        />
        <button
          type="button"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          @click="loadCredits"
        >
          Filtrar
        </button>
      </div>
    </div>

    <!-- Tabela -->
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Cliente</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Total financiado</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Parcelas</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Próximo venc.</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-white uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in credits" :key="item.id" class="hover:bg-orange-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ item.client_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">R$ {{ formatPrice(item.financed_amount) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
              {{ (item.installments_count - (item.pending_count || 0)) }}/{{ item.installments_count }}
              <span v-if="item.overdue_count" class="text-red-600 font-medium">({{ item.overdue_count }} atrasadas)</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
              {{ item.next_due_date ? formatDate(item.next_due_date) : '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusClass(item.status)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ item.status_display }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <router-link
                :to="{ name: 'CreditDetail', params: { id: item.id } }"
                class="text-orange-600 hover:text-orange-800 mr-4"
              >
                Ver
              </router-link>
              <button
                v-if="item.status === 'open' && item.pending_count > 0"
                type="button"
                class="text-green-600 hover:text-green-800"
                @click="router.push({ name: 'CreditDetail', params: { id: item.id } })"
              >
                Receber
              </button>
            </td>
          </tr>
          <tr v-if="loading">
            <td colspan="6" class="px-6 py-8 text-center text-gray-500">Carregando...</td>
          </tr>
          <tr v-else-if="credits.length === 0">
            <td colspan="6" class="px-6 py-8 text-center text-gray-500">Nenhum crediário encontrado</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Previsão de entrada pelas parcelas em aberto -->
    <div class="mt-4 bg-white rounded-lg shadow border-2 border-orange-200 p-4">
      <h2 class="text-sm font-semibold text-gray-700 mb-2">Previsão de entrada pelas parcelas em aberto</h2>
      <p class="text-2xl font-bold text-orange-600">R$ {{ formatPrice(forecastTotal) }}</p>
      <p class="text-xs text-gray-500 mt-1">Soma do valor das parcelas pendentes e atrasadas (crediários em aberto)</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { creditsService } from '@/services/credits'

const router = useRouter()
const route = useRoute()
const credits = ref([])
const loading = ref(false)
const forecastTotal = ref(0)
const filters = ref({
  status: '',
  q: '',
  start: '',
  end: '',
})

async function loadCredits() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.q) params.q = filters.value.q
    if (filters.value.start) params.start = filters.value.start
    if (filters.value.end) params.end = filters.value.end
    const res = await creditsService.getAll(params)
    credits.value = res.data.results ?? res.data
    if (Array.isArray(credits.value) === false) credits.value = []
    const forecastRes = await creditsService.getForecast(params)
    forecastTotal.value = forecastRes.data.forecast_total ?? 0
  } catch (err) {
    console.error(err)
    credits.value = []
    forecastTotal.value = 0
  } finally {
    loading.value = false
  }
}

function formatPrice(v) {
  if (v == null || isNaN(v)) return '0,00'
  return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('pt-BR')
}

function getStatusClass(status) {
  const map = {
    open: 'bg-amber-100 text-amber-800',
    settled: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

watch(
  () => route.query.status,
  (s) => {
    filters.value.status = s ?? ''
    loadCredits()
  },
  { immediate: true }
)
</script>
