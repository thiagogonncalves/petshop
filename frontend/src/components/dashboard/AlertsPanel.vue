<template>
  <div v-if="hasAlerts" class="bg-white rounded-xl shadow-md border-2 border-amber-200 overflow-hidden">
    <div class="bg-amber-100 px-4 py-3 border-b border-amber-200">
      <h2 class="text-lg font-bold text-amber-900 flex items-center">
        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        Alertas
      </h2>
    </div>
    <div class="p-4 space-y-4">
      <div v-if="alerts?.low_stock?.length" class="space-y-2">
        <h3 class="text-sm font-semibold text-gray-700">Estoque baixo</h3>
        <ul class="space-y-1">
          <li v-for="item in alerts.low_stock" :key="item.product_id"
              class="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
            <span class="text-sm text-gray-800">{{ item.name }}</span>
            <span class="text-sm font-bold text-red-600">{{ item.balance }} un.</span>
          </li>
        </ul>
        <router-link to="/reports/low-stock" class="text-orange-600 text-sm font-medium hover:underline block mt-2">
          Ver estoque completo
        </router-link>
      </div>
      <div v-if="alerts?.credit_due?.length" class="space-y-2">
        <h3 class="text-sm font-semibold text-gray-700">Parcelas vencendo/vencidas</h3>
        <ul class="space-y-1">
          <li v-for="item in alerts.credit_due" :key="item.installment_id"
              class="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
            <span class="text-sm text-gray-800">{{ item.client }}</span>
            <span class="text-sm font-bold" :class="item.status === 'OVERDUE' ? 'text-red-600' : 'text-amber-600'">
              R$ {{ formatPrice(item.amount) }} - {{ formatDate(item.due_date) }}
            </span>
          </li>
        </ul>
        <router-link to="/credits" class="text-orange-600 text-sm font-medium hover:underline block mt-2">
          Receber parcela
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  alerts: { type: Object, default: () => ({}) },
})

const hasAlerts = computed(() => {
  const a = props.alerts || {}
  return (a.low_stock?.length ?? 0) > 0 || (a.credit_due?.length ?? 0) > 0
})

function formatPrice(v) {
  return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v ?? 0)
}
function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR')
}
</script>
