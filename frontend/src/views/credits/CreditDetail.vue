<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Carregando...</div>
  <div v-else-if="account" class="space-y-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center">
        <router-link :to="{ name: 'CreditsList' }" class="text-orange-600 hover:text-orange-800 mr-4">
          ← Voltar
        </router-link>
        <h1 class="text-2xl font-bold text-gray-800">Crediário #{{ account.id }}</h1>
      </div>
      <span :class="getStatusClass(account.status)" class="px-3 py-1 text-sm font-semibold rounded-full">
        {{ account.status_display }}
      </span>
    </div>

    <!-- Cabeçalho -->
    <div class="bg-white rounded-lg shadow border border-gray-200 p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <p class="text-sm text-gray-500">Cliente</p>
          <p class="font-semibold text-gray-900">{{ account.client_name }}</p>
          <p class="text-sm text-gray-600">{{ account.client_document }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Venda #</p>
          <p class="font-semibold text-gray-900">{{ account.sale_id }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Total</p>
          <p class="font-semibold text-gray-900">R$ {{ formatPrice(account.total_amount) }}</p>
          <p v-if="account.down_payment > 0" class="text-xs text-gray-600">Entrada: R$ {{ formatPrice(account.down_payment) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Financiado</p>
          <p class="font-semibold text-orange-600">R$ {{ formatPrice(account.financed_amount) }}</p>
          <p class="text-xs text-gray-600">{{ account.installments_count }} parcelas</p>
        </div>
      </div>
    </div>

    <!-- Parcelas -->
    <div class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      <h2 class="px-6 py-3 bg-gray-50 font-semibold text-gray-800 border-b">Parcelas</h2>
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-6 py-2 text-left text-xs font-medium text-gray-600 uppercase">Nº</th>
            <th class="px-6 py-2 text-left text-xs font-medium text-gray-600 uppercase">Vencimento</th>
            <th class="px-6 py-2 text-left text-xs font-medium text-gray-600 uppercase">Valor</th>
            <th class="px-6 py-2 text-left text-xs font-medium text-gray-600 uppercase">Status</th>
            <th class="px-6 py-2 text-left text-xs font-medium text-gray-600 uppercase">Forma</th>
            <th class="px-6 py-2 text-left text-xs font-medium text-gray-600 uppercase">Pago em</th>
            <th class="px-6 py-2 text-right text-xs font-medium text-gray-600 uppercase">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="inst in account.installments || []" :key="inst.id" class="hover:bg-gray-50">
            <td class="px-6 py-3 text-sm font-medium text-gray-900">{{ inst.number }}/{{ account.installments_count }}</td>
            <td class="px-6 py-3 text-sm text-gray-600">{{ formatDate(inst.due_date) }}</td>
            <td class="px-6 py-3 text-sm font-medium text-gray-900">R$ {{ formatPrice(inst.amount) }}</td>
            <td class="px-6 py-3">
              <span :class="getInstallmentStatusClass(inst.status)" class="px-2 py-0.5 text-xs font-semibold rounded">
                {{ inst.status_display }}
              </span>
            </td>
            <td class="px-6 py-3 text-sm text-gray-600">
              {{ inst.status === 'paid' && inst.payment_method_display ? inst.payment_method_display : '-' }}
            </td>
            <td class="px-6 py-3 text-sm text-gray-600">
              {{ inst.paid_at ? formatDateTime(inst.paid_at) : '-' }}
              <span v-if="inst.paid_by_name" class="block text-xs text-gray-500">por {{ inst.paid_by_name }}</span>
            </td>
            <td class="px-6 py-3 text-right">
              <button
                v-if="(inst.status === 'pending' || inst.status === 'overdue') && !payingId"
                type="button"
                class="text-green-600 hover:text-green-800 font-medium text-sm"
                @click="openPayModal(inst)"
              >
                Receber
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Receber parcela -->
    <div v-if="payModal.installment" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="closePayModal">
      <div class="bg-white rounded-xl shadow-2xl max-w-sm w-full p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Receber parcela</h3>
        <p class="text-sm text-gray-600 mb-2">
          Parcela {{ payModal.installment.number }}/{{ account.installments_count }} – venc. {{ formatDate(payModal.installment.due_date) }}
        </p>
        <p class="text-xl font-bold text-orange-600 mb-4">R$ {{ formatPrice(payModal.installment.amount) }}</p>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Forma de pagamento</label>
          <select v-model="payModal.paymentMethod" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500" required>
            <option value="">Selecione...</option>
            <option value="cash">Dinheiro</option>
            <option value="pix">PIX</option>
            <option value="debit_card">Cartão de Débito</option>
            <option value="credit_card">Cartão de Crédito</option>
            <option value="bank_transfer">Transferência Bancária</option>
          </select>
        </div>
        <div class="flex gap-3">
          <button type="button" class="flex-1 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50" @click="closePayModal">
            Cancelar
          </button>
          <button
            type="button"
            class="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            :disabled="payingId || !payModal.paymentMethod"
            @click="confirmPay"
          >
            {{ payingId ? 'Processando...' : 'Confirmar pagamento' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-center py-12 text-gray-500">Crediário não encontrado</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { creditsService } from '@/services/credits'

const route = useRoute()
const account = ref(null)
const loading = ref(true)
const payingId = ref(null)
const payModal = ref({ installment: null, paymentMethod: '' })

const id = computed(() => route.params.id)

async function loadAccount() {
  loading.value = true
  try {
    const res = await creditsService.getById(id.value)
    account.value = res.data
  } catch {
    account.value = null
  } finally {
    loading.value = false
  }
}

function openPayModal(inst) {
  payModal.value = { installment: inst, paymentMethod: '' }
}

function closePayModal() {
  payModal.value = { installment: null, paymentMethod: '' }
}

async function confirmPay() {
  if (!payModal.value.installment || !payModal.value.paymentMethod) return
  payingId.value = payModal.value.installment.id
  try {
    await creditsService.payInstallment(payModal.value.installment.id, {
      amount: String(payModal.value.installment.amount),
      payment_method: payModal.value.paymentMethod,
    })
    closePayModal()
    await loadAccount()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao registrar pagamento')
  } finally {
    payingId.value = null
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

function formatDateTime(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function getStatusClass(status) {
  const map = {
    open: 'bg-amber-100 text-amber-800',
    settled: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

function getInstallmentStatusClass(status) {
  const map = {
    pending: 'bg-yellow-100 text-yellow-800',
    paid: 'bg-green-100 text-green-800',
    overdue: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

onMounted(() => loadAccount())
</script>
