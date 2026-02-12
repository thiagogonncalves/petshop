<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
      <div class="flex items-center">
        <svg class="w-6 h-6 sm:w-7 sm:h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11H6v-2h12v2zm0-4H6V8h12v2z"/>
        </svg>
        <h1 class="text-xl sm:text-2xl font-bold text-blue-800">Contas a pagar</h1>
      </div>
      <button
        type="button"
        :disabled="!subscriptionStore.canWrite"
        class="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation min-h-[44px] w-full sm:w-auto"
        @click="openModal()"
      >
        Nova conta
      </button>
    </div>

    <!-- Filtros -->
    <div class="bg-white rounded-lg shadow border border-gray-200 p-4 mb-4">
      <div class="flex flex-wrap gap-3">
        <select v-model="filters.status" class="px-3 py-2 border border-gray-300 rounded-lg text-sm" @change="loadBills">
          <option value="">Todos os status</option>
          <option value="pending">Pendente</option>
          <option value="overdue">Em atraso</option>
          <option value="paid">Pago</option>
          <option value="cancelled">Cancelado</option>
        </select>
        <button
          type="button"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          @click="loadBills"
        >
          Filtrar
        </button>
      </div>
    </div>

    <!-- Tabela -->
    <div class="bg-white shadow-lg rounded-lg overflow-x-auto border-2 theme-card -mx-3 sm:mx-0">
      <table class="min-w-[640px] w-full divide-y divide-gray-200">
        <thead class="theme-table-header">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Descrição</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Fornecedor</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Vencimento</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Valor</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-white uppercase tracking-wider whitespace-nowrap min-w-[200px]">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="bill in bills" :key="bill.id" class="hover:bg-orange-50">
            <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ bill.description }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ bill.provider || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(bill.due_date) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">R$ {{ formatPrice(bill.amount) }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusClass(bill.status)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ bill.status_display }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex flex-wrap gap-2 justify-end">
                <button
                  v-if="bill.status === 'pending' || bill.status === 'overdue'"
                  type="button"
                  :disabled="!subscriptionStore.canWrite"
                  class="text-green-600 hover:text-green-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  @click="markAsPaid(bill)"
                >
                  Marcar pago
                </button>
                <button
                  type="button"
                  :disabled="!subscriptionStore.canWrite"
                  class="text-blue-600 hover:text-blue-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  @click="openModal(bill)"
                >
                  Editar
                </button>
                <button
                  v-if="bill.status !== 'paid'"
                  type="button"
                  :disabled="!subscriptionStore.canWrite"
                  class="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed"
                  @click="deleteBill(bill)"
                >
                  Excluir
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="loading">
            <td colspan="6" class="px-6 py-8 text-center text-gray-500">Carregando...</td>
          </tr>
          <tr v-else-if="bills.length === 0">
            <td colspan="6" class="px-6 py-8 text-center text-gray-500">Nenhuma conta a pagar</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Nova/Editar -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 p-4 sm:p-0" @click.self="closeModal">
      <div class="relative top-4 sm:top-10 mx-auto p-4 sm:p-6 border-2 border-orange-300 w-full max-w-lg shadow-2xl rounded-xl bg-white">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11H6v-2h12v2zm0-4H6V8h12v2z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">{{ editingBill ? 'Editar conta' : 'Nova conta' }}</h3>
        </div>
        <form @submit.prevent="saveBill">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrição *</label>
              <input v-model="form.description" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Fornecedor</label>
              <input v-model="form.provider" type="text"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Valor (R$) *</label>
                <input v-model="form.amount" type="number" step="0.01" min="0.01" required
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Vencimento *</label>
                <input v-model="form.due_date" type="date" required
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              </div>
            </div>
            <div v-if="editingBill">
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select v-model="form.status"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="pending">Pendente</option>
                <option value="overdue">Em atraso</option>
                <option value="paid">Pago</option>
                <option value="cancelled">Cancelado</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Observações</label>
              <textarea v-model="form.observations" rows="2"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
            </div>
          </div>
          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { payablesService } from '@/services/payables'
import { useSubscriptionStore } from '@/stores/subscription'

const subscriptionStore = useSubscriptionStore()
const bills = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingBill = ref(null)
const filters = ref({ status: '' })

const form = ref({
  description: '',
  provider: '',
  amount: '',
  due_date: '',
  status: 'pending',
  observations: '',
})

async function loadBills() {
  loading.value = true
  try {
    const { data } = await payablesService.getAll({ status: filters.value.status || undefined })
    bills.value = data.results ?? data
  } catch {
    bills.value = []
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
  const dt = new Date(d)
  return dt.toLocaleDateString('pt-BR')
}

function getStatusClass(status) {
  const map = {
    pending: 'bg-amber-100 text-amber-800',
    overdue: 'bg-red-100 text-red-800',
    paid: 'bg-green-100 text-green-800',
    cancelled: 'bg-gray-100 text-gray-800',
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

function openModal(bill = null) {
  editingBill.value = bill
  if (bill) {
    form.value = {
      description: bill.description,
      provider: bill.provider || '',
      amount: bill.amount,
      due_date: bill.due_date,
      status: bill.status,
      observations: bill.observations || '',
    }
  } else {
    const today = new Date().toISOString().slice(0, 10)
    form.value = {
      description: '',
      provider: '',
      amount: '',
      due_date: today,
      status: 'pending',
      observations: '',
    }
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingBill.value = null
}

async function saveBill() {
  try {
    if (editingBill.value) {
      await payablesService.update(editingBill.value.id, form.value)
    } else {
      await payablesService.create(form.value)
    }
    closeModal()
    loadBills()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao salvar')
  }
}

async function markAsPaid(bill) {
  if (!confirm(`Marcar "${bill.description}" como pago?`)) return
  try {
    await payablesService.markPaid(bill.id)
    loadBills()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao marcar como pago')
  }
}

async function deleteBill(bill) {
  if (!confirm(`Excluir "${bill.description}"?`)) return
  try {
    await payablesService.delete(bill.id)
    loadBills()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao excluir')
  }
}

onMounted(() => loadBills())
</script>
