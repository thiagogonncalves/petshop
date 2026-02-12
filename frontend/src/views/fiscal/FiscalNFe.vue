<template>
  <div>
    <!-- Importar por chave e Sincronizar -->
    <div class="bg-white shadow-lg rounded-lg border-2 theme-card p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">Importar NF-e (SEFAZ)</h2>
      <p class="text-sm text-gray-600 mb-4">Importe NF-e pela chave de acesso (44 dígitos) ou sincronize automaticamente por NSU.</p>
      <div class="flex flex-wrap gap-4 items-end">
        <div class="flex-1 min-w-[280px]">
          <input
            v-model="accessKeyInput"
            type="text"
            placeholder="Chave de acesso (44 dígitos)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          />
          <p class="mt-1 text-xs text-gray-500">{{ accessKeyDigits.length }}/44 dígitos</p>
        </div>
        <button
          @click="importByKey"
          :disabled="accessKeyDigits.length !== 44 || loadingImport"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loadingImport ? 'Importando...' : 'Importar' }}
        </button>
        <button
          @click="sync"
          :disabled="loadingSync"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loadingSync ? 'Sincronizando...' : 'Sincronizar agora' }}
        </button>
      </div>
      <p v-if="importError" class="mt-2 text-sm text-red-600">{{ importError }}</p>
      <p v-if="syncMessage" class="mt-2 text-sm text-green-600">{{ syncMessage }}</p>
    </div>

    <!-- Filtros -->
    <div class="bg-white shadow rounded-lg border theme-card p-4 mb-4 flex flex-wrap gap-4">
      <div>
        <label class="block text-xs text-gray-500 mb-1">Status</label>
        <select
          v-model="filters.status"
          class="px-3 py-1.5 border border-gray-300 rounded-lg text-sm"
          @change="loadList"
        >
          <option value="">Todos</option>
          <option value="pending">Pendente</option>
          <option value="processing">Processando</option>
          <option value="imported">Importado</option>
          <option value="error">Erro</option>
        </select>
      </div>
    </div>

    <!-- Tabela -->
    <div class="bg-white shadow-lg rounded-lg border-2 theme-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-orange-100">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Chave</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Emitente</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Data</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Valor</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Status</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">XML</th>
              <th class="px-4 py-2 text-right text-xs font-medium text-orange-800">Ação</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="nfe in list" :key="nfe.id">
              <td class="px-4 py-2 text-sm text-gray-600 font-mono">{{ nfe.access_key?.slice(0, 20) }}...</td>
              <td class="px-4 py-2 text-sm text-gray-700">{{ nfe.emitente || '-' }}</td>
              <td class="px-4 py-2 text-sm text-gray-500">{{ formatDate(nfe.data_emissao) }}</td>
              <td class="px-4 py-2 text-sm">R$ {{ formatValor(nfe.valor_total) }}</td>
              <td class="px-4 py-2">
                <span :class="statusClass(nfe.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ statusLabel(nfe.status) }}
                </span>
              </td>
              <td class="px-4 py-2 text-sm">{{ nfe.tem_xml ? 'Sim' : '-' }}</td>
              <td class="px-4 py-2 text-right">
                <router-link
                  :to="{ name: 'FiscalNFeDetail', params: { id: nfe.id } }"
                  class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Ver
                </router-link>
              </td>
            </tr>
            <tr v-if="list.length === 0 && !loading">
              <td colspan="7" class="px-4 py-8 text-center text-gray-500">Nenhuma NF-e importada.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="hasNext" class="p-4 border-t flex justify-center">
        <button
          @click="loadMore"
          :disabled="loading"
          class="px-4 py-2 text-sm text-blue-600 hover:text-blue-800"
        >
          Carregar mais
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fiscalService } from '@/services/fiscal'

const accessKeyInput = ref('')
const accessKeyDigits = computed(() => (accessKeyInput.value || '').replace(/\D/g, ''))
const loadingImport = ref(false)
const loadingSync = ref(false)
const importError = ref('')
const syncMessage = ref('')
const list = ref([])
const loading = ref(false)
const nextPage = ref(null)
const filters = ref({ status: '' })

const hasNext = computed(() => !!nextPage.value)

async function importByKey() {
  if (accessKeyDigits.value.length !== 44) return
  loadingImport.value = true
  importError.value = ''
  try {
    await fiscalService.importByKey(accessKeyInput.value)
    accessKeyInput.value = ''
    loadList()
  } catch (err) {
    importError.value = err.response?.data?.error || 'Erro ao importar.'
  } finally {
    loadingImport.value = false
  }
}

async function sync() {
  loadingSync.value = true
  syncMessage.value = ''
  try {
    await fiscalService.sync()
    syncMessage.value = 'Sincronização iniciada. Atualize a lista em alguns segundos.'
    loadList()
  } catch (err) {
    importError.value = err.response?.data?.error || 'Erro ao sincronizar.'
  } finally {
    loadingSync.value = false
  }
}

async function loadList() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    const res = await fiscalService.listNFe(params)
    list.value = res.data.results ?? (Array.isArray(res.data) ? res.data : [])
    nextPage.value = res.data.next
  } catch {
    list.value = []
    nextPage.value = null
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!nextPage.value || loading.value) return
  loading.value = true
  try {
    const url = nextPage.value.startsWith('http') ? nextPage.value : window.location.origin + nextPage.value
    const page = new URL(url).searchParams.get('page')
    const params = { ...filters.value }
    if (page) params.page = page
    const res = await fiscalService.listNFe(params)
    list.value = [...list.value, ...(res.data.results ?? [])]
    nextPage.value = res.data.next
  } finally {
    loading.value = false
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

function formatDate(val) {
  if (!val) return '-'
  if (val.length > 10) {
    const d = new Date(val)
    return d.toLocaleDateString('pt-BR')
  }
  return val
}

function formatValor(val) {
  if (val == null || val === '-') return '0,00'
  return Number(val).toFixed(2).replace('.', ',')
}

onMounted(() => loadList())
</script>
