<template>
  <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden p-4 sm:p-5">
    <h2 class="text-lg font-bold text-gray-800 mb-4">Produtos mais vendidos (7 dias)</h2>
    <div v-if="!data?.length" class="h-32 flex items-center justify-center text-gray-400 text-sm">
      Nenhum dado
    </div>
    <div v-else class="space-y-2">
      <div
        v-for="(p, i) in data"
        :key="p.product_id"
        class="flex items-center gap-2"
      >
        <span class="text-gray-400 font-bold w-5">{{ i + 1 }}</span>
        <div class="flex-1 min-w-0">
          <div class="flex justify-between text-sm mb-0.5">
            <span class="font-medium text-gray-800 truncate">{{ p.name }}</span>
            <span class="text-orange-600 font-semibold flex-shrink-0 ml-2">{{ p.qty }} un.</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-1.5">
            <div
              class="bg-orange-500 h-1.5 rounded-full"
              :style="{ width: barWidth(p) }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const maxQty = computed(() => {
  const vals = props.data?.map(d => d.qty) ?? []
  return Math.max(...vals, 1)
})

function barWidth(p) {
  if (!maxQty.value || maxQty.value <= 0) return '0%'
  const pct = Math.min(100, (p.qty / maxQty.value) * 100)
  return `${pct}%`
}
</script>
