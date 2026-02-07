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
            <option value="count">Qtd vendas</option>
            <option value="items">Itens vendidos</option>
          </select>
        </div>
        <button
          @click="load"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
        >
          Atualizar
        </button>
      </div>
    </div>

    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 theme-card">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="theme-table-header">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase w-16">#</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Vendedor</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Vendas</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Itens</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Faturamento</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Ticket médio</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Cancel. %</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="(r, idx) in results" :key="r.user_id" class="hover:bg-orange-50">
            <td class="px-4 py-3 text-sm font-bold">
              <span v-if="idx === 0" class="text-yellow-600" title="1º">🥇</span>
              <span v-else-if="idx === 1" class="text-gray-500" title="2º">🥈</span>
              <span v-else-if="idx === 2" class="text-amber-700" title="3º">🥉</span>
              <span v-else class="text-gray-500">{{ idx + 1 }}</span>
            </td>
            <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ r.name || r.username }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.total_sales }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.items_sold }}</td>
            <td class="px-4 py-3 text-sm text-right font-medium">R$ {{ formatPrice(r.revenue) }}</td>
            <td class="px-4 py-3 text-sm text-right">R$ {{ formatPrice(r.ticket_avg) }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.cancellation_rate }}%</td>
          </tr>
          <tr v-if="results.length === 0 && !loading">
            <td colspan="7" class="px-4 py-8 text-center text-gray-500">Nenhum dado no período.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSalesRanking } from '@/services/reports'

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
    const res = await getSalesRanking({ start: start.value, end: end.value, order: order.value, limit: 50 })
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
