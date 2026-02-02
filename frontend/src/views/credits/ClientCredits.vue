<template>
  <div>
    <div class="flex items-center mb-6">
      <router-link :to="{ name: 'CreditsList' }" class="text-orange-600 hover:text-orange-800 mr-4">← Voltar</router-link>
      <h1 class="text-2xl font-bold text-gray-800">Histórico de Crediários – Cliente</h1>
    </div>
    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando...</div>
    <div v-else-if="clientName" class="mb-4">
      <p class="text-lg font-semibold text-gray-800">{{ clientName }}</p>
    </div>
    <div v-if="credits.length === 0" class="bg-white rounded-lg shadow border p-8 text-center text-gray-500">
      Nenhum crediário encontrado para este cliente.
    </div>
    <div v-else class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase">Data</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase">Venda #</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase">Total</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase">Financiado</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase">Parcelas</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-white uppercase">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="item in credits" :key="item.id" class="hover:bg-orange-50">
            <td class="px-6 py-4 text-sm text-gray-600">{{ formatDate(item.created_at) }}</td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900">#{{ item.sale_id }}</td>
            <td class="px-6 py-4 text-sm text-gray-700">R$ {{ formatPrice(item.total_amount) }}</td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900">R$ {{ formatPrice(item.financed_amount) }}</td>
            <td class="px-6 py-4 text-sm text-gray-600">{{ (item.installments_count - (item.pending_count || 0)) }}/{{ item.installments_count }}</td>
            <td class="px-6 py-4">
              <span :class="getStatusClass(item.status)" class="px-2 py-0.5 text-xs font-semibold rounded">
                {{ item.status_display }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <router-link :to="{ name: 'CreditDetail', params: { id: item.id } }" class="text-orange-600 hover:text-orange-800 font-medium text-sm">
                Ver
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { clientsService } from '@/services/clients'

const route = useRoute()
const credits = ref([])
const clientName = ref('')
const loading = ref(true)
const clientId = computed(() => route.params.clientId)

async function loadCredits() {
  loading.value = true
  try {
    const [credRes, clientRes] = await Promise.all([
      clientsService.getCredits(clientId.value),
      clientsService.getById(clientId.value),
    ])
    credits.value = credRes.data
    clientName.value = clientRes.data?.name || ''
  } catch {
    credits.value = []
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

onMounted(() => loadCredits())
</script>
