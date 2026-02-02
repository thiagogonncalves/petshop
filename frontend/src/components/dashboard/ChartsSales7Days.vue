<template>
  <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden p-4 sm:p-5">
    <h2 class="text-lg font-bold text-gray-800 mb-4">Vendas (últimos 7 dias)</h2>
    <div v-if="!data?.length" class="h-40 flex items-center justify-center text-gray-400 text-sm">
      Nenhum dado
    </div>
    <div v-else class="h-40 flex items-end gap-1 sm:gap-2">
      <div
        v-for="d in data"
        :key="d.date"
        class="flex-1 flex flex-col items-center gap-1"
      >
        <div
          class="w-full bg-orange-400 rounded-t hover:bg-orange-500 transition-colors min-h-[4px]"
          :style="{ height: barHeight(d) }"
          :title="`${formatDate(d.date)}: R$ ${formatPrice(d.value)}`"
        ></div>
        <span class="text-[10px] sm:text-xs text-gray-500 truncate w-full text-center">
          {{ formatDateShort(d.date) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const maxValue = computed(() => {
  const vals = props.data?.map(d => d.value) ?? []
  return Math.max(...vals, 1)
})

function barHeight(d) {
  if (!maxValue.value || maxValue.value <= 0) return '4px'
  const pct = Math.min(100, (d.value / maxValue.value) * 100)
  return `${Math.max(4, pct)}%`
}

function formatPrice(v) {
  return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v ?? 0)
}
function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR')
}
function formatDateShort(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}
</script>
