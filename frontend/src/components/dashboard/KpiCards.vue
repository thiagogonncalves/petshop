<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden hover:shadow-lg transition-shadow">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-orange-100 rounded-lg p-3">
            <svg class="h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4 flex-1">
            <dt class="text-sm font-medium text-gray-600">Vendas Hoje</dt>
            <dd class="text-2xl font-bold text-gray-900">{{ formatPrice(kpis?.sales_today ?? 0) }}</dd>
            <dd v-if="kpis?.sales_today_change_pct !== undefined" class="text-xs mt-1"
                :class="kpis.sales_today_change_pct >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ kpis.sales_today_change_pct >= 0 ? '+' : '' }}{{ kpis.sales_today_change_pct }}% vs ontem
            </dd>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden hover:shadow-lg transition-shadow">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-blue-100 rounded-lg p-3">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="ml-4 flex-1">
            <dt class="text-sm font-medium text-gray-600">Vendas no Mês</dt>
            <dd class="text-2xl font-bold text-gray-900">{{ formatPrice(kpis?.sales_month ?? 0) }}</dd>
            <div v-if="kpis?.sales_month_goal" class="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div class="bg-orange-500 h-2 rounded-full" :style="monthProgressStyle"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden hover:shadow-lg transition-shadow">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-green-100 rounded-lg p-3">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="ml-4 flex-1">
            <dt class="text-sm font-medium text-gray-600">Atendimentos Hoje</dt>
            <dd class="text-2xl font-bold text-gray-900">{{ kpis?.appointments_today_total ?? 0 }}</dd>
            <dd class="text-xs text-gray-500 mt-1">{{ kpis?.appointments_today_done ?? 0 }} concluídos</dd>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden hover:shadow-lg transition-shadow">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0 rounded-lg p-3" :class="creditAlertClass">
            <svg class="h-6 w-6" :class="creditAlertTextClass" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="ml-4 flex-1">
            <dt class="text-sm font-medium text-gray-600">Crediário em Aberto</dt>
            <dd class="text-2xl font-bold text-gray-900">{{ formatPrice(kpis?.credit_open_total ?? 0) }}</dd>
            <dd v-if="(kpis?.credit_overdue_count ?? 0) > 0" class="text-xs text-red-600 font-medium mt-1">
              {{ kpis.credit_overdue_count }} parcela(s) vencida(s)
            </dd>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  kpis: { type: Object, default: () => ({}) },
})

const creditAlertClass = computed(() =>
  (props.kpis?.credit_overdue_count ?? 0) > 0 ? 'bg-red-100' : 'bg-amber-100'
)
const creditAlertTextClass = computed(() =>
  (props.kpis?.credit_overdue_count ?? 0) > 0 ? 'text-red-600' : 'text-amber-600'
)

const monthProgressStyle = computed(() => {
  const goal = props.kpis?.sales_month_goal
  const current = props.kpis?.sales_month ?? 0
  if (!goal || goal <= 0) return { width: '0%' }
  const pct = Math.min(100, (current / goal) * 100)
  return { width: pct + '%' }
})

function formatPrice(v) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v ?? 0)
}
</script>
