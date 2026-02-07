<template>
  <div class="pdv-page min-h-screen flex flex-col bg-[#e8e8e8] fixed inset-0 w-full h-full z-40 overflow-auto">
    <!-- Barra do nome do produto (destaque) -->
    <div class="bg-[#1e3a5f] text-white px-6 py-5 text-center min-h-[72px] flex items-center justify-center">
      <span class="text-2xl font-semibold uppercase">{{ currentProduct ? currentProduct.name : 'Digite o código ou nome do produto' }}</span>
    </div>

    <!-- Área central: painel esquerdo + cupom -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 min-h-0">
      <!-- Coluna esquerda: foto + entrada do produto -->
      <div class="lg:col-span-1 flex flex-col gap-3">
        <div class="bg-white rounded-xl shadow-md border border-gray-200 p-4 flex flex-col gap-4">
          <!-- Foto do produto (acima do bloco do código) -->
          <div class="w-full flex justify-center">
            <div class="w-[224px] h-[224px] rounded-lg bg-gray-100 border-2 border-gray-200 flex items-center justify-center overflow-hidden flex-shrink-0">
              <template v-if="currentProduct?.image_url">
                <img :src="currentProduct.image_url" :alt="currentProduct.name" class="w-full h-full object-cover" />
              </template>
              <template v-else>
                <svg class="w-16 h-16 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
                <span class="sr-only">Sem foto</span>
              </template>
            </div>
          </div>
          <!-- Bloco do código e campos do produto -->
          <div class="space-y-2">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-0.5">Código</label>
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                type="text"
                placeholder="Código ou nome..."
                class="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-[#1e3a5f] focus:border-[#1e3a5f]"
                @keydown.enter.prevent="onSearchEnter"
                @input="onSearchInput"
              />
            </div>
            <!-- Para produto em KG: escolher unidade inteira ou venda por kg -->
            <div v-if="currentProduct?.unit === 'KG'" class="space-y-2 mb-2">
              <label class="block text-xs font-medium text-gray-600">Forma de venda</label>
              <div class="flex gap-4">
                <label class="flex items-center">
                  <input v-model="soldByKgChoice" type="radio" value="whole" class="mr-2">
                  <span class="text-sm">Unidade inteira</span>
                </label>
                <label class="flex items-center">
                  <input v-model="soldByKgChoice" type="radio" value="kg" class="mr-2">
                  <span class="text-sm">Venda por kg</span>
                </label>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-0.5">
                  {{ currentProduct?.unit === 'KG' && soldByKgChoice === 'kg' ? 'Quantidade (kg)' : 'Quantidade' }}
                </label>
                <input
                  v-model.number="quantityToAdd"
                  :type="(currentProduct?.unit === 'KG' && soldByKgChoice === 'kg') ? 'number' : 'number'"
                  :min="(currentProduct?.unit === 'KG' && soldByKgChoice === 'kg') ? 0.001 : 1"
                  :step="(currentProduct?.unit === 'KG' && soldByKgChoice === 'kg') ? 0.001 : 1"
                  class="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
                  @keydown.enter.prevent="addCurrentToCart"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-0.5">Preço Unit.</label>
                <input
                  v-model="unitPriceToAdd"
                  type="text"
                  placeholder="0,00"
                  class="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
                  @keydown.enter.prevent="addCurrentToCart"
                />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-0.5">Preço Total</label>
                <div class="w-full px-2 py-1.5 border border-gray-200 rounded text-sm bg-gray-50 text-gray-700">
                  {{ formatPrice(lineTotalToAdd) }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-0.5">Desconto</label>
                <input
                  v-model="discountToAdd"
                  type="text"
                  placeholder="0,00"
                  class="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
                  @keydown.enter.prevent="addCurrentToCart"
                />
              </div>
            </div>
            <button
              type="button"
              :disabled="!currentProduct || !subscriptionStore.canWrite"
              class="w-full py-2 bg-[#1e3a5f] text-white rounded-lg text-sm font-medium hover:bg-[#2a4a7a] disabled:opacity-50 disabled:cursor-not-allowed"
              @click="addCurrentToCart"
            >
              Adicionar
            </button>
          </div>
        </div>
        <!-- Sugestões -->
        <div v-if="suggestions.length > 0" class="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
          <div class="max-h-48 overflow-y-auto">
            <button
              v-for="p in suggestions"
              :key="p.id"
              type="button"
              class="w-full text-left px-3 py-2 hover:bg-blue-50 border-b border-gray-100 last:border-0 flex justify-between items-center text-sm"
              @click="selectProduct(p)"
            >
              <span class="font-medium text-gray-800 truncate flex-1">{{ p.name }}</span>
              <span class="text-[#1e3a5f] font-semibold ml-2">
                R$ {{ formatPrice(p.sale_price) }}
                <template v-if="p.unit === 'KG' && p.price_per_kg"> / {{ formatPrice(p.price_per_kg) }}/kg</template>
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Coluna direita: cupom (estilo recibo) -->
      <div class="lg:col-span-2 flex flex-col min-h-0">
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 flex flex-col flex-1 min-h-0 overflow-hidden">
          <div class="relative pt-4 px-4">
            <!-- Efeito recibo (bordas recortadas) -->
            <div class="absolute top-0 left-0 right-0 h-3 flex justify-between pointer-events-none">
              <span v-for="i in 20" :key="i" class="w-2 border border-gray-300 border-t-0 rounded-b-full bg-white" style="margin-left: -1px;"></span>
            </div>
          </div>
          <div class="px-4 pb-4 flex-1 overflow-y-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b-2 border-gray-200 text-gray-600 text-xs uppercase">
                  <th class="text-left py-2">Produto</th>
                  <th class="text-right w-16">Qtd</th>
                  <th class="text-right w-20">Unit.</th>
                  <th class="text-right w-20">Desc.</th>
                  <th class="text-right w-24">Total</th>
                  <th class="w-10"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(line, idx) in cart" :key="idx" class="border-b border-gray-100">
                  <td class="py-2 font-medium text-gray-800 uppercase">{{ line.name }}</td>
                  <td class="text-right">
                    <input
                      v-model.number="line.quantity"
                      type="number"
                      :min="line.sold_by_kg ? 0.001 : 1"
                      :step="line.sold_by_kg ? 0.001 : 1"
                      class="w-16 text-right border border-gray-300 rounded px-1 py-0.5 text-sm"
                      @change="normalizeQuantity(line)"
                    />
                  </td>
                  <td class="text-right text-gray-600">R$ {{ formatPrice(line.unit_price) }}</td>
                  <td class="text-right">
                    <input
                      v-model="line.discount"
                      type="number"
                      min="0"
                      step="0.01"
                      class="w-16 text-right border border-gray-300 rounded px-1 py-0.5 text-sm"
                      @input="normalizeDiscount(line)"
                    />
                  </td>
                  <td class="text-right font-medium">R$ {{ formatPrice(lineTotal(line)) }}</td>
                  <td>
                    <button
                      type="button"
                      class="text-red-600 hover:text-red-800 p-1"
                      title="Remover"
                      @click="removeFromCart(idx)"
                    >
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
                    </button>
                  </td>
                </tr>
                <tr v-if="cart.length === 0">
                  <td colspan="6" class="py-8 text-center text-gray-500">Nenhum item no carrinho</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="border-t-2 border-gray-200 bg-gray-50 px-4 py-3 space-y-1">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Subtotal</span>
              <span class="font-medium">R$ {{ formatPrice(subtotal) }}</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <label class="text-gray-600">Desconto (manual)</label>
              <input
                v-model="globalDiscount"
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                class="w-24 text-right border border-gray-300 rounded px-2 py-1"
              />
            </div>
            <div class="flex justify-between text-lg font-bold text-[#1e3a5f] pt-1">
              <span>Total</span>
              <span>R$ {{ formatPrice(cartTotal) }}</span>
            </div>
          </div>
          <div class="p-4">
            <button
              type="button"
              :disabled="cart.length === 0 || !subscriptionStore.canWrite"
              class="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold rounded-lg shadow transition-colors"
              @click="openCheckoutModal"
            >
              Finalizar compra
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer: barra azul com dados da empresa, atalhos e operador (uma linha) -->
    <footer class="bg-[#1e3a5f] text-white px-4 py-2.5 flex items-center justify-between gap-3 text-sm flex-nowrap shrink-0">
      <div class="flex items-center gap-3 flex-nowrap min-w-0">
        <template v-if="company.name || company.cpf_cnpj">
          <span class="font-semibold uppercase truncate">{{ company.name || 'GB PET' }}</span>
          <span v-if="company.cpf_cnpj" class="text-white/90 shrink-0">{{ company.cpf_cnpj }}</span>
          <span class="text-white/60 shrink-0">|</span>
        </template>
        <span class="shrink-0">F12 - Menu Fiscal</span>
        <span class="font-medium shrink-0">Caixa Aberto</span>
        <span class="text-white/60 shrink-0">|</span>
        <span class="shrink-0"><kbd class="px-1 py-0.5 bg-white/20 rounded text-xs">F3</kbd> Voltar</span>
        <span class="shrink-0"><kbd class="px-1 py-0.5 bg-white/20 rounded text-xs">F4</kbd> Consulta produto</span>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <span class="text-white/90">Atendido por:</span>
        <span class="font-semibold uppercase">{{ operatorName }}</span>
      </div>
    </footer>

    <!-- Modal Consulta de produto (F4) -->
    <div v-if="showConsultaModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto" @click.self="closeConsultaModal" @keydown.esc="closeConsultaModal">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col my-8" role="dialog" aria-label="Consulta de produto">
        <div class="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-800">Consulta de produto</h3>
          <button type="button" class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg" @click="closeConsultaModal" aria-label="Fechar">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
          </button>
        </div>
        <div class="p-4 border-b border-gray-200">
          <input
            ref="consultaInputRef"
            v-model="consultaQuery"
            type="text"
            placeholder="Digite código ou nome do produto..."
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1e3a5f] focus:border-[#1e3a5f] text-lg"
            autofocus
          />
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b-2 border-gray-200 text-gray-600 uppercase text-xs">
                <th class="text-left py-2 pr-4">Produto</th>
                <th class="text-left py-2 pr-4 w-24">Código</th>
                <th class="text-right py-2 pr-4 w-24">Estoque</th>
                <th class="text-right py-2 w-28">Preço</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in consultaResults" :key="p.id" class="border-b border-gray-100 hover:bg-gray-50">
                <td class="py-3 pr-4 font-medium text-gray-800">{{ p.name }}</td>
                <td class="py-3 pr-4 text-gray-600">{{ p.sku || p.gtin || '-' }}</td>
                <td class="py-3 pr-4 text-right text-gray-700">{{ p.stock_balance ?? p.stock_quantity ?? 0 }}</td>
                <td class="py-3 text-right font-semibold text-[#1e3a5f]">R$ {{ formatPrice(p.sale_price) }}</td>
              </tr>
              <tr v-if="consultaQuery.trim() && !consultaLoading && consultaResults.length === 0">
                <td colspan="4" class="py-8 text-center text-gray-500">Nenhum produto encontrado.</td>
              </tr>
              <tr v-else-if="!consultaQuery.trim()">
                <td colspan="4" class="py-8 text-center text-gray-500">Digite código ou nome para buscar.</td>
              </tr>
              <tr v-else-if="consultaLoading">
                <td colspan="4" class="py-8 text-center text-gray-500">Buscando...</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl text-sm text-gray-600">
          <kbd class="px-1.5 py-0.5 bg-gray-200 rounded">Esc</kbd> Fechar
        </div>
      </div>
    </div>

    <!-- Modal Finalizar -->
    <div v-if="showCheckoutModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto" @click.self="closeCheckoutModal">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 my-8">
        <h3 class="text-xl font-bold text-gray-800 mb-4">Finalizar venda</h3>
        <div class="space-y-4">
          <label v-if="checkout.paymentMethod !== 'crediario'" class="flex items-center gap-2">
            <input v-model="checkout.isWalkIn" type="checkbox" class="rounded border-gray-300 text-[#1e3a5f] focus:ring-[#1e3a5f]" />
            <span>Venda avulsa</span>
          </label>
          <p v-else class="text-sm text-amber-700 bg-amber-50 px-3 py-2 rounded-lg">Crediário exige cliente cadastrado. Venda avulsa bloqueada.</p>
          <div v-if="!checkout.isWalkIn || checkout.paymentMethod === 'crediario'">
            <label class="block text-sm font-medium text-gray-700 mb-1">CPF do cliente</label>
            <input
              v-model="checkout.cpf"
              type="text"
              placeholder="000.000.000-00"
              maxlength="14"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              @input="maskCpf"
            />
            <button
              type="button"
              class="mt-1 text-sm text-[#1e3a5f] hover:underline"
              @click="searchClientByCpf"
            >
              Buscar cliente
            </button>
            <p v-if="checkout.clientName" class="text-sm text-green-700 mt-1">{{ checkout.clientName }}</p>
            <p v-if="checkout.cpfError" class="text-sm text-red-600 mt-1">{{ checkout.cpfError }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Forma de pagamento</label>
            <select v-model="checkout.paymentMethod" class="w-full px-3 py-2 border border-gray-300 rounded-lg" @change="onPaymentMethodChange">
              <option value="cash">Dinheiro</option>
              <option value="pix">PIX</option>
              <option value="credit_card">Cartão de Crédito</option>
              <option value="debit_card">Cartão de Débito</option>
              <option value="bank_transfer">Transferência</option>
              <option value="crediario">Crediário da Casa</option>
            </select>
          </div>
          <div v-if="checkout.paymentMethod === 'crediario'" class="space-y-3 border-t pt-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Entrada (opcional)</label>
              <input
                v-model.number="checkout.downPayment"
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                @input="updateInstallmentPreview"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Número de parcelas (1–12)</label>
              <select v-model.number="checkout.installmentsCount" class="w-full px-3 py-2 border border-gray-300 rounded-lg" @change="updateInstallmentPreview">
                <option v-for="n in 12" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ checkout.installmentsCount === 1 ? 'Data de vencimento' : 'Primeiro vencimento' }}</label>
              <input
                v-model="checkout.firstDueDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                @change="updateInstallmentPreview"
              />
            </div>
            <div v-if="installmentPreview.length > 0" class="bg-gray-50 rounded-lg p-3 max-h-32 overflow-y-auto">
              <p class="text-xs font-medium text-gray-600 mb-2">Preview das parcelas</p>
              <p v-for="p in installmentPreview" :key="p.number" class="text-sm text-gray-700">
                {{ p.number }}/{{ installmentPreview.length }} – venc. {{ p.dueDate }} – R$ {{ p.amount }}
              </p>
            </div>
          </div>
        </div>
        <div class="mt-6 flex gap-3">
          <button type="button" class="flex-1 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50" @click="closeCheckoutModal">
            Cancelar
          </button>
          <button
            type="button"
            class="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            :disabled="checkoutSubmitting || !canConfirmSale"
            @click="confirmSale"
          >
            {{ checkoutSubmitting ? 'Processando...' : 'Confirmar venda' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { productsService } from '@/services/products'
import { clientsService } from '@/services/clients'
import { salesService } from '@/services/sales'
import { companyService } from '@/services/company'
import { useSubscriptionStore } from '@/stores/subscription'

const router = useRouter()
const subscriptionStore = useSubscriptionStore()
const authStore = useAuthStore()
const company = ref({})
const operatorName = computed(() => {
  const u = authStore.user
  if (!u) return 'Operador'
  const full = u.full_name || [u.first_name, u.last_name].filter(Boolean).join(' ').trim()
  return full || u.username || u.email || 'Operador'
})
const searchInputRef = ref(null)
const searchQuery = ref('')
const suggestions = ref([])
const currentProduct = ref(null)
const quantityToAdd = ref(1)
const soldByKgChoice = ref('whole')
const unitPriceToAdd = ref('')
const discountToAdd = ref('0')
const cart = ref([])
const globalDiscount = ref(0)
const showCheckoutModal = ref(false)
const checkoutSubmitting = ref(false)
const checkout = ref({
  isWalkIn: true,
  cpf: '',
  clientName: '',
  cpfError: '',
  paymentMethod: 'pix',
  downPayment: 0,
  installmentsCount: 6,
  firstDueDate: '',
})
const installmentPreview = ref([])

const showConsultaModal = ref(false)
const consultaQuery = ref('')
const consultaResults = ref([])
const consultaLoading = ref(false)
const consultaInputRef = ref(null)
let consultaDebounce = null

function openConsultaModal() {
  showConsultaModal.value = true
  consultaQuery.value = ''
  consultaResults.value = []
  nextTick(() => consultaInputRef.value?.focus())
}

function closeConsultaModal() {
  showConsultaModal.value = false
  consultaQuery.value = ''
  consultaResults.value = []
}

watch(consultaQuery, (q) => {
  if (consultaDebounce) clearTimeout(consultaDebounce)
  const trimmed = (q || '').trim()
  if (!trimmed) {
    consultaResults.value = []
    return
  }
  consultaDebounce = setTimeout(async () => {
    consultaLoading.value = true
    try {
      const { data } = await productsService.search(trimmed)
      consultaResults.value = Array.isArray(data) ? data : []
    } catch {
      consultaResults.value = []
    } finally {
      consultaLoading.value = false
    }
  }, 250)
})

function onKeydown(e) {
  if (e.key === 'F3') {
    e.preventDefault()
    router.push({ name: 'Dashboard' })
    return
  }
  if (e.key === 'F4') {
    e.preventDefault()
    openConsultaModal()
    return
  }
  if (e.key === 'Escape' && showConsultaModal.value) {
    e.preventDefault()
    closeConsultaModal()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', onKeydown)
  try {
    const { data } = await companyService.get()
    company.value = data || {}
  } catch {
    company.value = {}
  }
  subscriptionStore.fetchStatus().catch(() => {})
  nextTick(() => searchInputRef.value?.focus())
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})

function getDefaultFirstDueDate() {
  const d = new Date()
  d.setDate(d.getDate() + 30)
  return d.toISOString().slice(0, 10)
}

function onPaymentMethodChange() {
  if (checkout.value.paymentMethod === 'crediario') {
    checkout.value.isWalkIn = false
    if (!checkout.value.firstDueDate) checkout.value.firstDueDate = getDefaultFirstDueDate()
    updateInstallmentPreview()
    if (checkout.value.cpf.replace(/\D/g, '').length === 11) searchClientByCpf()
  }
}

function updateInstallmentPreview() {
  if (checkout.value.paymentMethod !== 'crediario') return
  const total = cartTotal.value
  const down = Number(checkout.value.downPayment) || 0
  const n = Number(checkout.value.installmentsCount) || 6
  const firstDate = checkout.value.firstDueDate
  if (!firstDate || n < 1 || total <= down) {
    installmentPreview.value = []
    return
  }
  const financed = total - down
  const baseAmount = Math.floor((financed / n) * 100) / 100
  const preview = []
  let cumulative = 0
  for (let i = 1; i <= n; i++) {
    let amount = baseAmount
    if (i === n) amount = Math.round((financed - cumulative) * 100) / 100
    else cumulative += amount
    const d = new Date(firstDate)
    d.setMonth(d.getMonth() + i - 1)
    const dueDate = d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
    preview.push({ number: i, dueDate, amount: amount.toFixed(2).replace('.', ',') })
  }
  installmentPreview.value = preview
}

const canConfirmSale = computed(() => {
  if (checkout.value.paymentMethod === 'crediario') {
    const cpfOk = checkout.value.cpf.replace(/\D/g, '').length === 11
    const clientOk = !!checkout.value.clientName
    const dateOk = !!checkout.value.firstDueDate
    const instOk = (Number(checkout.value.installmentsCount) || 0) >= 1
    return cpfOk && clientOk && dateOk && instOk
  }
  if (!checkout.value.isWalkIn) {
    return checkout.value.cpf.replace(/\D/g, '').length === 11 && !!checkout.value.clientName
  }
  return true
})

function parseDecimal(str) {
  if (str === '' || str == null) return 0
  const n = Number(String(str).replace(',', '.'))
  return isNaN(n) ? 0 : n
}

const lineTotalToAdd = computed(() => {
  const qty = parseFloat(quantityToAdd.value) || 0
  const price = parseDecimal(unitPriceToAdd.value)
  return Math.max(0, qty * price)
})

const subtotal = computed(() => {
  return cart.value.reduce((sum, l) => sum + lineTotal(l), 0)
})

function lineTotal(line) {
  const qty = parseFloat(line.quantity) || 0
  const price = Number(line.unit_price) || 0
  const disc = Number(line.discount) || 0
  return Math.max(0, qty * price - disc)
}

const cartTotal = computed(() => {
  const disc = Number(globalDiscount.value) || 0
  return Math.max(0, subtotal.value - disc)
})

watch(currentProduct, (p) => {
  if (p) {
    soldByKgChoice.value = 'whole'
    unitPriceToAdd.value = String(p.sale_price ?? 0).replace('.', ',')
    quantityToAdd.value = 1
    discountToAdd.value = '0'
  }
}, { immediate: true })

watch(soldByKgChoice, (val) => {
  const p = currentProduct.value
  if (!p || p.unit !== 'KG') return
  if (val === 'whole') {
    unitPriceToAdd.value = String(p.sale_price ?? 0).replace('.', ',')
    quantityToAdd.value = 1
  } else {
    unitPriceToAdd.value = String(p.price_per_kg ?? 0).replace('.', ',')
    quantityToAdd.value = 0.5
  }
})

let searchDebounce = null
function onSearchInput() {
  if (searchDebounce) clearTimeout(searchDebounce)
  const q = searchQuery.value.trim()
  if (!q) {
    suggestions.value = []
    return
  }
  const isNumeric = /^\d+$/.test(q)
  if (isNumeric && q.length >= 8) {
    searchDebounce = setTimeout(() => {
      productsService.byCode(q).then(({ data }) => {
        suggestions.value = [data]
        currentProduct.value = data
      }).catch(() => {
        suggestions.value = []
        currentProduct.value = null
      })
    }, 100)
    return
  }
  searchDebounce = setTimeout(() => {
    productsService.search(q).then(({ data }) => {
      const list = Array.isArray(data) ? data : []
      suggestions.value = list
      currentProduct.value = list[0] || null
    }).catch(() => {
      suggestions.value = []
      currentProduct.value = null
    })
  }, 250)
}

function selectProduct(p) {
  currentProduct.value = p
  searchQuery.value = p.name || ''
  suggestions.value = []
  nextTick(() => searchInputRef.value?.focus())
}

function onSearchEnter() {
  const q = searchQuery.value.trim()
  if (!q) return
  const isNumeric = /^\d+$/.test(q)
  if (isNumeric && q.length >= 8) {
    productsService.byCode(q).then(({ data }) => {
      currentProduct.value = data
      addCurrentToCart()
      searchQuery.value = ''
      suggestions.value = []
      nextTick(() => searchInputRef.value?.focus())
    }).catch(() => {})
    return
  }
  if (suggestions.value.length > 0) {
    currentProduct.value = suggestions.value[0]
    addCurrentToCart()
    searchQuery.value = ''
    suggestions.value = []
    nextTick(() => searchInputRef.value?.focus())
  }
}

function addCurrentToCart() {
  const p = currentProduct.value
  if (!p) return
  const isKgProduct = p.unit === 'KG'
  const sellByKg = isKgProduct && soldByKgChoice.value === 'kg'
  const qty = sellByKg
    ? Math.max(0.001, parseFloat(quantityToAdd.value) || 0.001)
    : Math.max(1, parseInt(quantityToAdd.value) || 1)
  const price = parseDecimal(unitPriceToAdd.value) || (sellByKg ? parseFloat(p.price_per_kg) : parseFloat(p.sale_price)) || 0.01
  const disc = Math.max(0, parseDecimal(discountToAdd.value))
  const existing = cart.value.find(l => l.product_id === p.id && l.unit_price === price && l.sold_by_kg === sellByKg)
  if (existing) {
    existing.quantity = (parseFloat(existing.quantity) || 0) + qty
    existing.discount = (Number(existing.discount) || 0) + disc
  } else {
    cart.value.push({
      product_id: p.id,
      name: p.name + (sellByKg ? ' (kg)' : ''),
      unit_price: price,
      quantity: qty,
      discount: disc,
      sold_by_kg: sellByKg,
    })
  }
  searchQuery.value = ''
  suggestions.value = []
  quantityToAdd.value = sellByKg ? 0.5 : 1
  unitPriceToAdd.value = sellByKg ? String(p.price_per_kg ?? 0).replace('.', ',') : String(p.sale_price ?? 0).replace('.', ',')
  discountToAdd.value = '0'
  nextTick(() => searchInputRef.value?.focus())
}

function normalizeQuantity(line) {
  const min = line.sold_by_kg ? 0.001 : 1
  if (parseFloat(line.quantity) < min) line.quantity = min
}

function normalizeDiscount(line) {
  const d = Number(line.discount)
  if (isNaN(d) || d < 0) line.discount = 0
}

function removeFromCart(idx) {
  cart.value.splice(idx, 1)
}

function formatPrice(v) {
  if (v == null || isNaN(v)) return '0,00'
  return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function openCheckoutModal() {
  checkout.value = {
    isWalkIn: true,
    cpf: '',
    clientName: '',
    cpfError: '',
    paymentMethod: 'pix',
    downPayment: 0,
    installmentsCount: 6,
    firstDueDate: getDefaultFirstDueDate(),
  }
  installmentPreview.value = []
  showCheckoutModal.value = true
}

function closeCheckoutModal() {
  showCheckoutModal.value = false
}

function maskCpf() {
  const digits = checkout.value.cpf.replace(/\D/g, '').slice(0, 11)
  let formatted = ''
  if (digits.length > 9) formatted = `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`
  else if (digits.length > 6) formatted = `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`
  else if (digits.length > 3) formatted = `${digits.slice(0, 3)}.${digits.slice(3)}`
  else formatted = digits
  checkout.value.cpf = formatted
  checkout.value.cpfError = ''
  checkout.value.clientName = ''
}

function searchClientByCpf() {
  const cpf = checkout.value.cpf.replace(/\D/g, '')
  if (cpf.length !== 11) {
    checkout.value.cpfError = 'CPF deve ter 11 dígitos'
    return
  }
  clientsService.byCpf(cpf).then(({ data }) => {
    checkout.value.clientName = data.name
    checkout.value.cpfError = ''
  }).catch(() => {
    checkout.value.clientName = ''
    checkout.value.cpfError = 'Cliente não encontrado'
  })
}

function confirmSale() {
  const items = cart.value.map(l => ({
    product_id: l.product_id,
    quantity: String(parseFloat(l.quantity) || 1),
    sold_by_kg: Boolean(l.sold_by_kg),
    unit_price: String(l.unit_price),
    discount: String(Number(l.discount) || 0),
  }))
  const payload = {
    is_walk_in: checkout.value.paymentMethod === 'crediario' ? false : checkout.value.isWalkIn,
    items,
    payment_method: checkout.value.paymentMethod,
    discount: String(Number(globalDiscount.value) || 0),
  }
  const cpfDigits = checkout.value.cpf.replace(/\D/g, '')
  if (checkout.value.paymentMethod === 'crediario') {
    payload.client_cpf = cpfDigits
    payload.down_payment = String(Number(checkout.value.downPayment) || 0)
    payload.installments_count = Number(checkout.value.installmentsCount) || 6
    payload.first_due_date = checkout.value.firstDueDate
  } else if (!checkout.value.isWalkIn && cpfDigits) {
    payload.cpf = cpfDigits
  }
  checkoutSubmitting.value = true
  salesService.pdvCreate(payload).then(({ data }) => {
    closeCheckoutModal()
    cart.value = []
    globalDiscount.value = 0
    const saleId = data.id
    router.push({ name: 'ReceiptPrint', params: { id: String(saleId) } })
    nextTick(() => searchInputRef.value?.focus())
  }).catch((err) => {
    const res = err.response?.data
    const msg = res?.items || res?.cpf || res?.is_walk_in || res?.installments_count || res?.first_due_date || res?.detail || 'Erro ao finalizar venda'
    alert(Array.isArray(msg) ? msg[0] : (typeof msg === 'object' ? JSON.stringify(msg) : msg))
  }).finally(() => {
    checkoutSubmitting.value = false
  })
}
</script>
