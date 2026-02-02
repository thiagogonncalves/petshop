<template>
  <div class="space-y-4">
    <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden">
      <div class="bg-orange-50 px-4 py-3 border-b border-orange-200">
        <h2 class="text-lg font-bold text-orange-900">Top Clientes do Mês</h2>
      </div>
      <div v-if="!topClients?.length" class="p-6 text-center text-gray-500 text-sm">Nenhum dado este mês</div>
      <ul v-else class="divide-y divide-gray-100">
        <li v-for="(c, i) in topClients" :key="c.client_id"
            class="flex items-center justify-between px-4 py-3 hover:bg-orange-50">
          <div class="flex items-center gap-2">
            <span class="text-gray-400 font-bold w-6">{{ i + 1 }}.</span>
            <span class="font-medium text-gray-800">{{ c.name }}</span>
          </div>
          <span class="text-orange-600 font-semibold">R$ {{ formatPrice(c.revenue) }}</span>
        </li>
      </ul>
      <router-link v-if="topClients?.length" to="/reports/top-clients"
                  class="block px-4 py-2 text-orange-600 text-sm font-medium hover:bg-orange-50 text-center">
        Ver todos
      </router-link>
    </div>

    <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden">
      <div class="bg-orange-50 px-4 py-3 border-b border-orange-200">
        <h2 class="text-lg font-bold text-orange-900">Clientes Inativos</h2>
        <p class="text-xs text-gray-600 mt-0.5">Sem visita há 60+ dias</p>
      </div>
      <div v-if="!inactiveClients?.length" class="p-6 text-center text-gray-500 text-sm">Nenhum cliente inativo</div>
      <ul v-else class="divide-y divide-gray-100">
        <li v-for="c in inactiveClients" :key="c.client_id"
            class="flex items-center justify-between px-4 py-3 hover:bg-orange-50">
          <span class="font-medium text-gray-800">{{ c.name }}</span>
          <span class="text-sm text-gray-500">{{ c.days_inactive }} dias</span>
        </li>
      </ul>
      <router-link v-if="inactiveClients?.length" to="/clients"
                  class="block px-4 py-2 text-orange-600 text-sm font-medium hover:bg-orange-50 text-center">
        Ver clientes
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  customers: { type: Object, default: () => ({}) },
})

const topClients = computed(() => props.customers?.top_clients_month ?? [])
const inactiveClients = computed(() => props.customers?.inactive_clients ?? [])

function formatPrice(v) {
  return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v ?? 0)
}
</script>
