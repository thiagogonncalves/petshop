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
          <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
          <select v-model="categoryId" class="rounded border-gray-300 shadow-sm min-w-[160px]">
            <option value="">Todas</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ordenar por</label>
          <select v-model="order" class="rounded border-gray-300 shadow-sm">
            <option value="revenue">Receita</option>
            <option value="qty">Quantidade</option>
            <option value="profit">Lucro</option>
          </select>
        </div>
        <button @click="load" class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">Filtrar</button>
        <button @click="exportCsv" :disabled="exporting" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {{ exporting ? "Exportando..." : "Exportar CSV" }}
        </button>
      </div>
    </div>
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Produto</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Categoria</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Qtd vendida</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Receita</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Preço médio</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Lucro est.</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Participação %</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="r in results" :key="r.product_id" class="hover:bg-orange-50">
            <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ r.name }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ r.category_name || "-" }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.quantity_total }}</td>
            <td class="px-4 py-3 text-sm text-right font-medium">R$ {{ formatPrice(r.revenue_total) }}</td>
            <td class="px-4 py-3 text-sm text-right">R$ {{ formatPrice(r.avg_price) }}</td>
            <td class="px-4 py-3 text-sm text-right text-green-700">R$ {{ formatPrice(r.estimated_profit) }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.share_percent }}%</td>
          </tr>
          <tr v-if="results.length === 0 && !loading">
            <td colspan="7" class="px-4 py-8 text-center text-gray-500">Nenhum produto vendido no período.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { getProductsSold, exportProductsSoldCsv } from "@/services/reports"
import api from "@/services/api"

const start = ref("")
const end = ref("")
const categoryId = ref("")
const order = ref("revenue")
const categories = ref([])
const results = ref([])
const loading = ref(false)
const exporting = ref(false)

function setDefaultPeriod() {
  const today = new Date()
  const past = new Date(today)
  past.setDate(past.getDate() - 29)
  start.value = past.toISOString().slice(0, 10)
  end.value = today.toISOString().slice(0, 10)
}

function formatPrice(v) {
  if (v == null) return "0,00"
  return Number(v).toFixed(2).replace(".", ",")
}

async function load() {
  loading.value = true
  try {
    const params = { start: start.value, end: end.value, order: order.value, limit: 200 }
    if (categoryId.value) params.category_id = categoryId.value
    const res = await getProductsSold(params)
    results.value = res.results || []
  } catch (e) {
    console.error(e)
    results.value = []
  } finally {
    loading.value = false
  }
}

async function exportCsv() {
  exporting.value = true
  try {
    const params = { start: start.value, end: end.value, order: order.value }
    if (categoryId.value) params.category_id = categoryId.value
    await exportProductsSoldCsv(params)
  } catch (e) {
    console.error(e)
    alert("Erro ao exportar CSV.")
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  setDefaultPeriod()
  try {
    const r = await api.get("/products/categories/")
    categories.value = r.data.results || r.data || []
  } catch {
    categories.value = []
  }
  await load()
})
</script>
