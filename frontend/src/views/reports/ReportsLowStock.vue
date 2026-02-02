<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg border border-orange-200 p-4">
      <div class="flex flex-wrap items-end gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Limite (opcional)</label>
          <input v-model.number="threshold" type="number" min="0" placeholder="Ex: 5" class="rounded border-gray-300 shadow-sm w-24" />
          <p class="text-xs text-gray-500 mt-1">Deixe vazio para usar estoque mínimo do produto</p>
        </div>
        <button @click="load" class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">Atualizar</button>
      </div>
    </div>

    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Produto</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">SKU</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-white uppercase">Categoria</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Saldo</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Mínimo</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase">Sugestão reposição</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="r in results" :key="r.id" class="hover:bg-orange-50">
            <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ r.name }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ r.sku || '-' }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ r.category_name || '-' }}</td>
            <td class="px-4 py-3 text-sm text-right font-medium" :class="r.stock_quantity <= 0 ? 'text-red-600' : ''">{{ r.stock_quantity }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.min_stock }}</td>
            <td class="px-4 py-3 text-sm text-right">{{ r.suggestion }}</td>
          </tr>
          <tr v-if="results.length === 0 && !loading">
            <td colspan="6" class="px-4 py-8 text-center text-gray-500">Nenhum produto com estoque baixo.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLowStock } from '@/services/reports'

const threshold = ref('')
const results = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const params = threshold.value !== '' && threshold.value != null ? { threshold: threshold.value } : {}
    const res = await getLowStock(params)
    results.value = res.results || []
  } catch (e) {
    console.error(e)
    results.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
</script>
