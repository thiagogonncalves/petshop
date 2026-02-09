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
          <label class="block text-sm font-medium text-gray-700 mb-1">Vendedor</label>
          <select v-model="userId" class="rounded border-gray-300 shadow-sm min-w-[140px]">
            <option value="">Todos</option>
            <option v-for="u in sellers" :key="u.id" :value="u.id">{{ u.name || u.username }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="status" class="rounded border-gray-300 shadow-sm">
            <option value="">Pagos</option>
            <option value="paid">Pago</option>
            <option value="pending">Pendente</option>
            <option value="cancelled">Cancelado</option>
            <option value="refunded">Reembolsado</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Busca</label>
          <input v-model="search" type="text" placeholder="ID, cliente..." class="rounded border-gray-300 shadow-sm w-40" />
        </div>
        <label class="flex items-center gap-2">
          <input v-model="includeCancelled" type="checkbox" class="rounded border-gray-300" />
          <span class="text-sm">Incluir canceladas</span>
        </label>
        <button
          @click="load(1)"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
        >
          Filtrar
        </button>
        <button
          @click="exportCsv"
          :disabled="exporting"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {{ exporting ? 'Exportando...' : 'Exportar CSV' }}
        </button>
      </div>
    </div>

    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 theme-card">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="theme-table-header">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">ID</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Data</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Vendedor</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Cliente</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Total</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Pagamento</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Status</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Ação</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr
            v-for="s in sales"
            :key="s.id"
            :class="[
              'hover:bg-orange-50',
              s.status === 'cancelled' ? 'bg-red-50/50' : ''
            ]"
          >
            <td class="px-4 py-3 text-sm font-medium" :class="s.status === 'cancelled' ? 'line-through text-red-700' : 'text-gray-900'">#{{ s.id }}</td>
            <td class="px-4 py-3 text-sm" :class="s.status === 'cancelled' ? 'line-through text-red-600' : 'text-gray-600'">{{ formatDate(s.sale_date) }}</td>
            <td class="px-4 py-3 text-sm" :class="s.status === 'cancelled' ? 'line-through text-red-600' : 'text-gray-600'">{{ s.created_by_name || '-' }}</td>
            <td class="px-4 py-3 text-sm" :class="s.status === 'cancelled' ? 'line-through text-red-600' : 'text-gray-600'">{{ s.client_name || '-' }}</td>
            <td class="px-4 py-3 text-sm text-right font-medium" :class="s.status === 'cancelled' ? 'line-through text-red-600' : ''">R$ {{ formatPrice(s.total) }}</td>
            <td class="px-4 py-3 text-sm" :class="s.status === 'cancelled' ? 'line-through text-red-600' : 'text-gray-600'">{{ s.payment_method_display }}</td>
            <td class="px-4 py-3">
              <span :class="statusClass(s.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                {{ s.status_display }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button
                v-if="s.status === 'cancelled' && s.cancellation_reason"
                type="button"
                class="text-red-600 hover:text-red-800 hover:underline text-sm mr-2"
                @click="showReasonModal = true; reasonToShow = s.cancellation_reason"
              >
                Ver motivo
              </button>
              <router-link :to="{ name: 'Sales', query: { id: s.id } }" class="text-blue-600 hover:underline text-sm">
                Ver
              </router-link>
            </td>
          </tr>
          <tr v-if="sales.length === 0 && !loading">
            <td colspan="8" class="px-4 py-8 text-center text-gray-500">Nenhuma venda no período.</td>
          </tr>
        </tbody>
      </table>
    <!-- Modal motivo do cancelamento -->
    <div v-if="showReasonModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showReasonModal = false">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 class="text-lg font-bold text-red-800 mb-2">Motivo do cancelamento</h3>
        <p class="text-gray-700 whitespace-pre-wrap">{{ reasonToShow || '-' }}</p>
        <div class="mt-4">
          <button
            type="button"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-gray-800"
            @click="showReasonModal = false"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>

    <Pagination
        v-if="totalPages > 1"
        :current-page="page"
        :total-pages="totalPages"
        :total-items="totalItems"
        :items-per-page="pageSize"
        @page-change="load"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSales, getSellers, exportSalesCsv } from '@/services/reports'
import Pagination from '@/components/Pagination.vue'

const start = ref('')
const end = ref('')
const userId = ref('')
const status = ref('')
const search = ref('')
const includeCancelled = ref(true)
const sellers = ref([])
const sales = ref([])
const loading = ref(false)
const exporting = ref(false)
const page = ref(1)
const pageSize = ref(20)
const totalPages = ref(1)
const totalItems = ref(0)
const showReasonModal = ref(false)
const reasonToShow = ref('')

function setDefaultPeriod() {
  const today = new Date()
  const past = new Date(today)
  past.setDate(past.getDate() - 29)
  start.value = past.toISOString().slice(0, 10)
  end.value = today.toISOString().slice(0, 10)
}

function formatDate(v) {
  if (!v) return '-'
  return new Date(v).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function formatPrice(v) {
  if (v == null) return '0,00'
  return Number(v).toFixed(2).replace('.', ',')
}

function statusClass(s) {
  const map = {
    pending: 'bg-yellow-100 text-yellow-800',
    paid: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    refunded: 'bg-gray-100 text-gray-800',
  }
  return map[s] || 'bg-gray-100 text-gray-800'
}

async function load(p = 1) {
  loading.value = true
  try {
    const params = { start: start.value, end: end.value, page: p, page_size: pageSize.value }
    if (userId.value) params.user_id = userId.value
    if (status.value) params.status = status.value
    if (search.value) params.q = search.value
    if (includeCancelled.value) params.include_cancelled = 'true'
    const res = await getSales(params)
    sales.value = res.results || []
    totalItems.value = res.count ?? res.results?.length ?? 0
    totalPages.value = Math.ceil(totalItems.value / pageSize.value) || 1
    page.value = p
  } catch (e) {
    console.error(e)
    sales.value = []
  } finally {
    loading.value = false
  }
}

async function exportCsv() {
  exporting.value = true
  try {
    const params = { start: start.value, end: end.value }
    if (userId.value) params.user_id = userId.value
    if (status.value) params.status = status.value
    if (includeCancelled.value) params.include_cancelled = 'true'
    await exportSalesCsv(params)
  } catch (e) {
    console.error(e)
    alert('Erro ao exportar CSV.')
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  setDefaultPeriod()
  try {
    sellers.value = await getSellers()
  } catch {
    sellers.value = []
  }
  await load(1)
})
</script>
