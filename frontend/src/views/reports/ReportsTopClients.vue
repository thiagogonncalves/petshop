<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg border border-orange-200 p-4">
      <div class="flex flex-wrap items-end gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Início</label>
          <input v-model="start" type="date" class="rounded border-gray-300 shadow-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fim</label>
          <input v-model="end" type="date" class="rounded border-gray-300 shadow-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ordenar por</label>
          <select v-model="order" class="rounded border-gray-300 shadow-sm">
            <option value="revenue">Faturamento</option>
            <option value="count">Qtd compras</option>
          </select>
        </div>
        <button @click="load" class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">Atualizar</button>
      </div>
    </div>

    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Cliente</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Compras</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Gasto total</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Ticket médio</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="r in results" :key="r.client_id" class="hover:bg-orange-50">
            <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ r.name }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.total_sales }}</td>
            <td class="px-4 py-3 text-sm text-right font-medium">R$ {{ formatPrice(r.total_revenue) }}</td>
            <td class="px-4 py-3 text-sm text-right">R$ {{ formatPrice(r.ticket_avg) }}</td>
          </tr>
          <tr v-if="results.length === 0 && !loading">
            <td colspan="4" class="px-4 py-8 text-center text-gray-500">Nenhum dado no período.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTopClients } from '@/services/reports'

const start = ref('')
const end = ref('')
const order = ref('revenue')
const results = ref([])
const loading = ref(false)

function setDefaultPeriod() {
  const today = new Date()
  const past = new Date(today)
  past.setDate(past.getDate() - 29)
  start.value = past.toISOString().slice(0, 10)
  end.value = today.toISOString().slice(0, 10)
}

function formatPrice(v) {
  if (v == null) return '0,00'
  return Number(v).toFixed(2).replace('.', ',')
}

async function load() {
  loading.value = true
  try {
    const res = await getTopClients({ start: start.value, end: end.value, order: order.value, limit: 50 })
    results.value = res.results || []
  } catch (e) {
    console.error(e)
    results.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  setDefaultPeriod()
  load()
})
</script>
