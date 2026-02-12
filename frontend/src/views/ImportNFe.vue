<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Importar NF-e</h1>
      </div>
    </div>

    <!-- Upload XML -->
    <div class="bg-white shadow-lg rounded-lg border-2 theme-card p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">Enviar arquivo XML da NF-e</h2>
      <form @submit.prevent="uploadXml" class="flex flex-wrap items-end gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            type="file"
            ref="fileInput"
            accept=".xml"
            @change="onFileSelect"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-orange-100 file:text-orange-800"
          />
        </div>
        <button
          type="submit"
          :disabled="!selectedFile || uploading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ uploading ? 'Enviando...' : 'Importar XML' }}
        </button>
      </form>
      <p v-if="uploadError" class="mt-2 text-sm text-red-600">{{ uploadError }}</p>
    </div>

    <!-- Importar pela chave de acesso -->
    <div class="bg-white shadow-lg rounded-lg border-2 theme-card p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">Ou importar pela chave de acesso</h2>
      <p class="text-sm text-gray-600 mb-3">Informe os 44 dígitos da chave de acesso da NF-e para buscar via SEFAZ (requer certificado A1 em Administração > Configuração SEFAZ).</p>
      <form @submit.prevent="importByKey" class="flex flex-wrap items-end gap-4">
        <div class="flex-1 min-w-[280px]">
          <input
            v-model="accessKeyInput"
            type="text"
            placeholder="Ex: 35210112345678000190550010000000011234567890"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          />
          <p class="mt-1 text-xs text-gray-500">{{ accessKeyDigits.length }}/44 dígitos</p>
        </div>
        <button
          type="submit"
          :disabled="accessKeyDigits.length !== 44 || loadingByKey"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loadingByKey ? 'Buscando...' : 'Buscar e importar' }}
        </button>
      </form>
      <p v-if="byKeyError" class="mt-2 text-sm text-red-600">{{ byKeyError }}</p>
      <p v-if="byKeySuccess" class="mt-2 text-sm text-green-600">{{ byKeySuccess }}</p>
    </div>

    <!-- Lista de importações -->
    <div class="bg-white shadow-lg rounded-lg border-2 theme-card overflow-hidden mb-6">
      <h2 class="text-lg font-semibold text-gray-800 p-4 border-b border-orange-200">Importações recentes</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-orange-100">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Chave</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Fornecedor</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Status</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-orange-800">Data</th>
              <th class="px-4 py-2 text-right text-xs font-medium text-orange-800">Ação</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="imp in imports" :key="imp.id">
              <td class="px-4 py-2 text-sm text-gray-600 font-mono">{{ imp.access_key?.slice(0, 20) }}...</td>
              <td class="px-4 py-2 text-sm text-gray-700">{{ imp.supplier_name || '-' }}</td>
              <td class="px-4 py-2">
                <span :class="statusClass(imp.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ imp.status === 'pending' ? 'Pendente' : imp.status === 'confirmed' ? 'Confirmado' : 'Cancelado' }}
                </span>
              </td>
              <td class="px-4 py-2 text-sm text-gray-500">{{ formatDate(imp.imported_at) }}</td>
              <td class="px-4 py-2 text-right">
                <button
                  v-if="imp.status === 'pending'"
                  @click="openConfirm(imp)"
                  class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Confirmar entrada
                </button>
                <span v-else class="text-gray-400 text-sm">-</span>
              </td>
            </tr>
            <tr v-if="imports.length === 0">
              <td colspan="5" class="px-4 py-6 text-center text-gray-500">Nenhuma importação. Envie um XML acima.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Confirmar entrada -->
    <div v-if="confirming" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeConfirm">
      <div class="relative top-6 mx-auto p-6 border-2 border-orange-300 w-full max-w-4xl shadow-2xl rounded-xl bg-white max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold text-blue-800 mb-4">Confirmar entrada de estoque</h3>
        <p class="text-sm text-gray-600 mb-4">Vincule cada item a um produto (ou deixe em branco para criar novo) e defina a margem %.</p>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-orange-100">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-orange-800">Produto (NF-e)</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-orange-800">Qtd</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-orange-800">Custo un.</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-orange-800">Vincular produto</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-orange-800">Margem %</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-orange-800">Preço venda</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="item in confirmItems" :key="item.id">
                <td class="px-3 py-2 text-sm text-gray-700">{{ item.product_name }}</td>
                <td class="px-3 py-2 text-sm">{{ item.quantity }} {{ item.unit }}</td>
                <td class="px-3 py-2 text-sm">R$ {{ formatPrice(item.unit_cost) }}</td>
                <td class="px-3 py-2">
                  <select
                    v-model="item.product_id"
                    class="w-full text-sm border border-gray-300 rounded px-2 py-1"
                  >
                    <option :value="null">Criar novo produto</option>
                    <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>
                </td>
                <td class="px-3 py-2">
                  <input
                    v-model.number="item.profit_margin"
                    type="number"
                    step="0.5"
                    min="0"
                    class="w-20 text-sm border border-gray-300 rounded px-2 py-1"
                  />
                </td>
                <td class="px-3 py-2 text-sm font-medium">
                  R$ {{ formatPrice(calculatedSalePrice(item)) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex justify-end gap-3 mt-4">
          <button type="button" @click="closeConfirm" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
            Cancelar
          </button>
          <button
            @click="submitConfirm"
            :disabled="confirmingLoading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ confirmingLoading ? 'Confirmando...' : 'Confirmar entrada' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { nfeService } from '@/services/nfe'
import { fiscalService } from '@/services/fiscal'
import { productsService } from '@/services/products'

const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadError = ref('')
const accessKeyInput = ref('')
const loadingByKey = ref(false)
const byKeyError = ref('')
const byKeySuccess = ref('')
const accessKeyDigits = computed(() => (accessKeyInput.value || '').replace(/\D/g, ''))
const imports = ref([])
const products = ref([])
const confirming = ref(null)
const confirmItems = ref([])
const confirmingLoading = ref(false)

function onFileSelect(e) {
  const f = e.target.files?.[0]
  selectedFile.value = f || null
  uploadError.value = ''
}

async function uploadXml() {
  if (!selectedFile.value) return
  uploading.value = true
  uploadError.value = ''
  try {
    const res = await nfeService.importXml(selectedFile.value)
    imports.value = [res.data, ...imports.value]
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  } catch (err) {
    uploadError.value = err.response?.data?.error || 'Erro ao importar XML'
  } finally {
    uploading.value = false
  }
}

async function importByKey() {
  if (accessKeyDigits.value.length !== 44) return
  loadingByKey.value = true
  byKeyError.value = ''
  byKeySuccess.value = ''
  try {
    await fiscalService.importByKey(accessKeyInput.value)
    byKeySuccess.value = 'NF-e enviada para importação via SEFAZ. O processamento ocorre em segundo plano.'
    accessKeyInput.value = ''
    setTimeout(() => { byKeySuccess.value = '' }, 5000)
  } catch (err) {
    byKeyError.value = err.response?.data?.error || 'Erro ao importar pela chave. Verifique o certificado em Administração > Configuração SEFAZ.'
  } finally {
    loadingByKey.value = false
  }
}

async function loadImports() {
  try {
    const res = await nfeService.list()
    imports.value = res.data.results ?? (Array.isArray(res.data) ? res.data : [])
  } catch {
    imports.value = []
  }
}

async function loadProducts() {
  try {
    const res = await productsService.getAll()
    products.value = res.data.results ?? (Array.isArray(res.data) ? res.data : [])
  } catch {
    products.value = []
  }
}

function statusClass(status) {
  if (status === 'confirmed') return 'bg-green-100 text-green-800'
  if (status === 'pending') return 'bg-yellow-100 text-yellow-800'
  return 'bg-gray-100 text-gray-800'
}

function formatDate(val) {
  if (!val) return '-'
  return new Date(val).toLocaleString('pt-BR')
}

function formatPrice(val) {
  if (val == null) return '0,00'
  return Number(val).toFixed(2).replace('.', ',')
}

function calculatedSalePrice(item) {
  const cost = Number(item.unit_cost)
  const margin = Number(item.profit_margin) || 0
  return cost * (1 + margin / 100)
}

function normalizeForMatch(str) {
  if (!str || typeof str !== 'string') return ''
  return str.toLowerCase().trim().replace(/\s+/g, ' ')
}

function findProductForItem(item, productsList) {
  if (!productsList || !productsList.length) return null
  const gtin = item.gtin && String(item.gtin).trim()
  if (gtin && gtin !== '' && gtin.toUpperCase() !== 'SEM GTIN') {
    const byGtin = productsList.find(
      (p) => (p.gtin && String(p.gtin).trim() === gtin) || (p.barcode && String(p.barcode).trim() === gtin)
    )
    if (byGtin) return byGtin.id
  }
  const name = normalizeForMatch(item.product_name)
  if (!name) return null
  const byName = productsList.find((p) => normalizeForMatch(p.name) === name)
  if (byName) return byName.id
  const partial = productsList.find((p) => normalizeForMatch(p.name).includes(name) || name.includes(normalizeForMatch(p.name)))
  return partial ? partial.id : null
}

async function openConfirm(imp) {
  try {
    const res = await nfeService.getById(imp.id)
    const full = res.data
    confirming.value = full
    const items = full.items || []
    confirmItems.value = items.map((it) => {
      const productId = findProductForItem(it, products.value) ?? it.product ?? null
      return {
        id: it.id,
        product_name: it.product_name,
        quantity: it.quantity,
        unit: it.unit,
        unit_cost: it.unit_cost,
        gtin: it.gtin,
        product_id: productId,
        profit_margin: 30,
      }
    })
    if (items.length === 0) {
      alert('Esta importação não possui itens.')
    }
  } catch (err) {
    alert(err.response?.data?.error || 'Erro ao carregar detalhes da importação.')
  }
}

function closeConfirm() {
  confirming.value = null
  confirmItems.value = []
}

async function submitConfirm() {
  if (!confirming.value) return
  if (!confirmItems.value.length) {
    alert('Nenhum item para confirmar. Recarregue a página e tente novamente.')
    return
  }
  const payload = {
    items: confirmItems.value.map((it) => ({
      id: it.id,
      product_id: it.product_id != null && it.product_id !== '' ? Number(it.product_id) : null,
      profit_margin: it.profit_margin != null ? Number(it.profit_margin) : 30,
    })),
  }
  if (payload.items.some((i) => i.id == null || i.id === undefined)) {
    alert('Erro nos itens: cada item precisa ter um id. Feche o modal e abra novamente "Confirmar entrada".')
    return
  }
  confirmingLoading.value = true
  try {
    await nfeService.confirm(confirming.value.id, payload.items)
    await loadImports()
    closeConfirm()
  } catch (err) {
    const msg = err.response?.data?.error || 'Erro ao confirmar entrada'
    alert(msg)
  } finally {
    confirmingLoading.value = false
  }
}

onMounted(() => {
  loadImports()
  loadProducts()
})
</script>
