<template>
  <div class="space-y-6">
    <!-- Filtros -->
    <div class="bg-white shadow rounded-lg border border-orange-200 p-4">
      <div class="flex flex-wrap items-end gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Período rápido</label>
          <select
            v-model="periodPreset"
            @change="applyPreset"
            class="rounded border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"
          >
            <option value="today">Hoje</option>
            <option value="yesterday">Ontem</option>
            <option value="7">Últimos 7 dias</option>
            <option value="30">Últimos 30 dias</option>
            <option value="month">Mês atual</option>
            <option value="custom">Personalizado</option>
          </select>
        </div>
        <div v-if="periodPreset === 'custom'" class="flex gap-2 items-end">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Início</label>
            <input v-model="start" type="date" class="rounded border-gray-300 shadow-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fim</label>
            <input v-model="end" type="date" class="rounded border-gray-300 shadow-sm" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Vendedor</label>
          <select
            v-model="userId"
            class="rounded border-gray-300 shadow-sm min-w-[160px]"
          >
            <option value="">Todos</option>
            <option v-for="u in sellers" :key="u.id" :value="u.id">{{ u.name || u.username }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Forma de pagamento</label>
          <select
            v-model="paymentMethod"
            class="rounded border-gray-300 shadow-sm"
          >
            <option value="">Todas</option>
            <option value="cash">Dinheiro</option>
            <option value="credit_card">Cartão de Crédito</option>
            <option value="debit_card">Cartão de Débito</option>
            <option value="pix">PIX</option>
            <option value="bank_transfer">Transferência</option>
            <option value="installment">Parcelado</option>
          </select>
        </div>
        <button
          @click="load"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
        >
          Aplicar
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-500">Carregando...</div>
    <template v-else-if="data">
      <!-- KPIs -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
          <p class="text-sm text-gray-600">Total de vendas</p>
          <p class="text-2xl font-bold text-blue-800">{{ data.total_sales }}</p>
        </div>
        <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
          <p class="text-sm text-gray-600">Faturamento</p>
          <p class="text-2xl font-bold text-blue-800">R$ {{ formatPrice(data.total_revenue) }}</p>
        </div>
        <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
          <p class="text-sm text-gray-600">Ticket médio</p>
          <p class="text-2xl font-bold text-blue-800">R$ {{ formatPrice(data.ticket_avg) }}</p>
        </div>
        <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
          <p class="text-sm text-gray-600">Itens vendidos</p>
          <p class="text-2xl font-bold text-blue-800">{{ data.total_items_sold }}</p>
        </div>
        <div v-if="data.estimated_profit != null" class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
          <p class="text-sm text-gray-600">Lucro estimado</p>
          <p class="text-2xl font-bold text-green-700">R$ {{ formatPrice(data.estimated_profit) }}</p>
        </div>
      </div>

      <!-- Vendas por dia (barras simples) -->
      <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
        <h2 class="text-lg font-semibold text-blue-800 mb-4">Vendas por dia</h2>
        <div v-if="data.sales_by_day && data.sales_by_day.length" class="space-y-2 max-h-64 overflow-y-auto">
          <div
            v-for="d in data.sales_by_day"
            :key="d.date"
            class="flex items-center gap-2"
          >
            <span class="text-sm text-gray-600 w-24">{{ d.date }}</span>
            <div class="flex-1 bg-gray-200 rounded h-6 overflow-hidden">
              <div
                class="bg-orange-500 h-full rounded"
                :style="{ width: barWidth(d.total) + '%' }"
              />
            </div>
            <span class="text-sm font-medium w-20 text-right">R$ {{ formatPrice(d.total) }}</span>
          </div>
        </div>
        <p v-else class="text-gray-500 text-sm">Nenhum dado no período.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Por forma de pagamento -->
        <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
          <h2 class="text-lg font-semibold text-blue-800 mb-4">Por forma de pagamento</h2>
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b">
                <th class="text-left py-2">Forma</th>
                <th class="text-right py-2">Qtd</th>
                <th class="text-right py-2">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in (data.sales_by_payment_method || [])" :key="row.payment_method" class="border-b border-gray-100">
                <td class="py-2">{{ paymentLabel(row.payment_method) }}</td>
                <td class="text-right py-2">{{ row.count }}</td>
                <td class="text-right py-2">R$ {{ formatPrice(row.total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Top 5 produtos -->
        <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
          <h2 class="text-lg font-semibold text-blue-800 mb-4">Top 5 produtos</h2>
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b">
                <th class="text-left py-2">Produto</th>
                <th class="text-right py-2">Qtd</th>
                <th class="text-right py-2">Receita</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in (data.top_5_products || [])" :key="p.product_id" class="border-b border-gray-100">
                <td class="py-2">{{ p.name }}</td>
                <td class="text-right py-2">{{ p.qty }}</td>
                <td class="text-right py-2">R$ {{ formatPrice(p.revenue) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Top 5 clientes -->
      <div class="bg-white rounded-lg border-2 border-orange-200 p-4 shadow">
        <h2 class="text-lg font-semibold text-blue-800 mb-4">Top 5 clientes</h2>
        <table class="min-w-full text-sm">
          <thead>
            <tr class="border-b">
              <th class="text-left py-2">Cliente</th>
              <th class="text-right py-2">Compras</th>
              <th class="text-right py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in (data.top_5_clients || [])" :key="c.client_id" class="border-b border-gray-100">
              <td class="py-2">{{ c.name }}</td>
              <td class="text-right py-2">{{ c.count }}</td>
              <td class="text-right py-2">R$ {{ formatPrice(c.total) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard, getSellers } from '@/services/reports'

const periodPreset = ref('30')
const start = ref('')
const end = ref('')
const userId = ref('')
const paymentMethod = ref('')
const sellers = ref([])
const data = ref(null)
const loading = ref(false)

function setDates(s, e) {
  start.value = s
  end.value = e
}

function applyPreset() {
  const today = new Date()
  const y = today.getFullYear()
  const m = String(today.getMonth() + 1).padStart(2, '0')
  const d = String(today.getDate()).padStart(2, '0')
  const todayStr = `${y}-${m}-${d}`

  if (periodPreset.value === 'today') {
    setDates(todayStr, todayStr)
  } else if (periodPreset.value === 'yesterday') {
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const ys = yesterday.toISOString().slice(0, 10)
    setDates(ys, ys)
  } else if (periodPreset.value === '7') {
    const past = new Date(today)
    past.setDate(past.getDate() - 6)
    setDates(past.toISOString().slice(0, 10), todayStr)
  } else if (periodPreset.value === '30') {
    const past = new Date(today)
    past.setDate(past.getDate() - 29)
    setDates(past.toISOString().slice(0, 10), todayStr)
  } else if (periodPreset.value === 'month') {
    setDates(`${y}-${m}-01`, todayStr)
  }
}

function barWidth(total) {
  if (!data.value || !data.value.sales_by_day || !data.value.sales_by_day.length) return 0
  const max = Math.max(...data.value.sales_by_day.map((x) => Number(x.total)))
  return max ? (Number(total) / max) * 100 : 0
}

function formatPrice(v) {
  if (v == null) return '0,00'
  return Number(v).toFixed(2).replace('.', ',')
}

function paymentLabel(key) {
  const map = {
    cash: 'Dinheiro',
    credit_card: 'Cartão de Crédito',
    debit_card: 'Cartão de Débito',
    pix: 'PIX',
    bank_transfer: 'Transferência',
    installment: 'Parcelado',
  }
  return map[key] || key
}

async function load() {
  loading.value = true
  try {
    const params = { start: start.value, end: end.value }
    if (userId.value) params.user_id = userId.value
    if (paymentMethod.value) params.payment_method = paymentMethod.value
    data.value = await getDashboard(params)
  } catch (e) {
    console.error(e)
    data.value = null
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  applyPreset()
  try {
    sellers.value = await getSellers()
  } catch {
    sellers.value = []
  }
  await load()
})
</script>
