<template>
  <div v-if="nfe" class="max-w-4xl">
    <div class="mb-4">
      <router-link to="/fiscal/nfe" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
        ← Voltar à lista
      </router-link>
    </div>

    <div class="bg-white shadow-lg rounded-lg border-2 theme-card overflow-hidden">
      <div class="p-6 border-b">
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-xl font-bold text-gray-800">NF-e {{ nfe.access_key?.slice(0, 20) }}...</h2>
            <span :class="statusClass(nfe.status)" class="inline-block mt-2 px-3 py-1 text-sm font-medium rounded-full">
              {{ statusLabel(nfe.status) }}
            </span>
          </div>
          <button
            v-if="nfe.tem_xml && authStore.isAdmin"
            @click="downloadXml"
            :disabled="downloadingXml"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm disabled:opacity-50"
          >
            {{ downloadingXml ? 'Baixando...' : 'Baixar XML' }}
          </button>
        </div>
      </div>

      <!-- Resumo -->
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Resumo</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-500">Chave</span>
            <p class="font-mono text-sm break-all">{{ nfe.access_key }}</p>
          </div>
          <div class="p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-500">Emitente</span>
            <p class="text-sm">{{ nfe.resumo?.emitente || '-' }}</p>
          </div>
          <div class="p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-500">Destinatário</span>
            <p class="text-sm">{{ nfe.resumo?.destinatario || '-' }}</p>
          </div>
          <div class="p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-500">Data emissão</span>
            <p class="text-sm">{{ nfe.resumo?.data_emissao || '-' }}</p>
          </div>
          <div class="p-3 bg-gray-50 rounded-lg">
            <span class="text-xs text-gray-500">Valor total</span>
            <p class="text-sm font-semibold">R$ {{ formatValor(nfe.resumo?.valor_total) }}</p>
          </div>
        </div>
      </div>

      <!-- Itens -->
      <div v-if="nfe.items?.length" class="p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Itens</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">#</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Descrição</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Qtd</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Unit.</th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Total</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="item in nfe.items" :key="item.id">
                <td class="px-3 py-2 text-sm">{{ item.item_number }}</td>
                <td class="px-3 py-2 text-sm">{{ item.description }}</td>
                <td class="px-3 py-2 text-sm">{{ item.qty }}</td>
                <td class="px-3 py-2 text-sm">R$ {{ formatValor(item.unit_price) }}</td>
                <td class="px-3 py-2 text-sm text-right">R$ {{ formatValor(item.total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="nfe.tem_xml" class="p-6 text-gray-500 text-sm">
        NF-e importada com XML, mas sem itens parseados (pode ser resumo resNFe).
      </div>
    </div>
  </div>
  <div v-else class="text-gray-500">Carregando...</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fiscalService } from '@/services/fiscal'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const nfe = ref(null)
const downloadingXml = ref(false)

async function downloadXml() {
  if (!nfe.value?.id) return
  downloadingXml.value = true
  try {
    const { default: api } = await import('@/services/api')
    const res = await api.get(`/fiscal/nfe/${nfe.value.id}/xml/`, { responseType: 'blob' })
    const blob = new Blob([res.data], { type: 'application/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `nfe_${nfe.value.access_key}.xml`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    alert(err.response?.data?.detail || 'Erro ao baixar XML')
  } finally {
    downloadingXml.value = false
  }
}

async function load() {
  const id = route.params.id
  if (!id) return
  try {
    const res = await fiscalService.getNFeById(id)
    nfe.value = res.data
  } catch {
    nfe.value = null
  }
}

function statusClass(s) {
  if (s === 'imported') return 'bg-green-100 text-green-800'
  if (s === 'processing' || s === 'pending') return 'bg-yellow-100 text-yellow-800'
  if (s === 'error') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

function statusLabel(s) {
  const m = { pending: 'Pendente', processing: 'Processando', imported: 'Importado', error: 'Erro' }
  return m[s] || s
}

function formatValor(val) {
  if (val == null) return '0,00'
  return Number(val).toFixed(2).replace('.', ',')
}

onMounted(() => load())
</script>
