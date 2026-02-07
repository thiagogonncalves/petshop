<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Produtos</h1>
      </div>
      <div class="flex gap-3">
        <router-link
          to="/nfe"
          :class="['px-4 py-2 rounded-lg shadow-md inline-flex items-center', subscriptionStore.canWrite ? 'bg-orange-500 text-white hover:bg-orange-600' : 'bg-gray-400 text-gray-200 pointer-events-none']"
        >
          Importar NF-e
        </router-link>
        <button
          type="button"
          :disabled="!subscriptionStore.canWrite"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          @click="openModal()"
        >
          Novo Produto
        </button>
      </div>
    </div>

    <!-- Campo de busca -->
    <div class="mb-4">
      <div class="relative max-w-md">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por nome, código, categoria, custo, preço, estoque ou status..."
          class="w-full pl-10 pr-4 py-2.5 rounded-lg border-2 border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-colors"
        />
        <button
          v-if="searchQuery"
          type="button"
          @click="searchQuery = ''"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          aria-label="Limpar busca"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Tabela de Produtos -->
    <div class="bg-white shadow-lg rounded-lg overflow-x-auto border-2 theme-card">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="theme-table-header">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider w-14">Foto</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Código</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Categoria</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Custo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Preço</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Estoque</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-white uppercase tracking-wider whitespace-nowrap sticky right-0 bg-orange-400 z-10">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="product in products" :key="product.id" class="hover:bg-orange-50/50">
            <td class="px-2 py-2 whitespace-nowrap">
              <div class="w-10 h-10 rounded border border-gray-200 bg-gray-100 flex items-center justify-center overflow-hidden">
                <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="w-full h-full object-cover" />
                <svg v-else class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ product.sku || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ product.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ product.category_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">R$ {{ formatPrice(product.cost_price) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">R$ {{ formatPrice(product.sale_price) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span :class="product.is_low_stock ? 'text-red-600 font-semibold' : 'text-gray-500'">
                {{ product.unit === 'KG' ? (product.stock_quantity / 1000).toFixed(3) : product.stock_quantity }} {{ product.unit === 'KG' ? 'kg' : product.unit }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" 
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ product.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-right sticky right-0 bg-white z-10 border-l border-gray-200">
              <button type="button" :disabled="!subscriptionStore.canWrite" class="mr-2 px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed" @click="openModal(product)">
                Editar
              </button>
              <button type="button" :disabled="!subscriptionStore.canWrite" class="px-3 py-1.5 rounded-lg bg-red-50 text-red-700 hover:bg-red-100 font-medium text-sm border border-red-200 disabled:opacity-50 disabled:cursor-not-allowed" @click="deleteProduct(product.id)">
                Excluir
              </button>
            </td>
          </tr>
          <tr v-if="loading && products.length === 0">
            <td colspan="9" class="px-6 py-8 text-center text-sm text-gray-500">Carregando...</td>
          </tr>
          <tr v-else-if="!loading && products.length === 0">
            <td colspan="9" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum produto encontrado</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação -->
    <Pagination
      v-if="totalCount > 0"
      :current-page="currentPage"
      :total-pages="totalPages"
      :total-items="totalCount"
      :items-per-page="pageSize"
      @page-change="goToPage"
    />

    <!-- Modal de Produto -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeModal">
      <div class="relative top-10 mx-auto p-6 border-2 border-orange-300 w-full max-w-2xl shadow-2xl rounded-xl bg-white">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">{{ editingProduct ? 'Editar Produto' : 'Novo Produto' }}</h3>
        </div>
        
        <form @submit.prevent="saveProduct">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Foto do produto</label>
            <div class="flex items-start gap-4">
              <div class="w-24 h-24 rounded-lg border-2 border-gray-200 bg-gray-50 flex items-center justify-center overflow-hidden flex-shrink-0">
                <img v-if="imagePreviewUrl" :src="imagePreviewUrl" alt="Preview" class="w-full h-full object-cover" />
                <svg v-else class="w-10 h-10 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <input
                  ref="fileInputRef"
                  type="file"
                  accept="image/*"
                  class="block w-full text-sm text-gray-500 file:mr-2 file:py-2 file:px-4 file:rounded file:border-0 file:bg-orange-100 file:text-orange-700 hover:file:bg-orange-200"
                  @change="onImageSelect"
                />
                <p class="text-xs text-gray-500 mt-1">PNG, JPG ou GIF. Opcional.</p>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input v-model="form.name" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrição (opcional)</label>
              <textarea v-model="form.description" rows="2" placeholder="Descrição do produto"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
              <div class="flex gap-2">
                <select v-model="form.category" required
                        class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                  <option value="">Selecione...</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                </select>
                <button type="button" @click="openCategoryModal()"
                        class="px-3 py-2 text-orange-600 border border-orange-300 rounded-md hover:bg-orange-50 text-sm whitespace-nowrap">
                  + Nova
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Código</label>
              <input v-model="form.sku" type="text" placeholder="Código do produto"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Código de Barras</label>
              <input v-model="form.barcode" type="text" placeholder="Código de barras"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço de Custo</label>
              <input v-model="form.cost_price" type="number" step="0.01" min="0" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Margem de Lucro (%)</label>
              <input v-model="form.profit_margin" type="number" step="0.5" min="0"
                     :disabled="form.price_manually_set"
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ form.unit === 'KG' ? 'Preço produto fechado (R$)' : 'Preço de Venda' }}</label>
              <input v-model="form.sale_price" type="number" step="0.01" min="0.01" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <p v-if="form.unit === 'KG'" class="text-xs text-gray-500 mt-0.5">Valor da unidade inteira</p>
            </div>
            <div v-if="form.unit === 'KG'" class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço por kg (R$)</label>
              <input v-model="form.price_per_kg" type="number" step="0.01" min="0"
                     class="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div class="flex items-end pb-2">
              <label class="flex items-center">
                <input v-model="form.price_manually_set" type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                <span class="ml-2 text-sm text-gray-700">Preço definido manualmente (não recalcular pela margem)</span>
              </label>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ form.unit === 'KG' ? 'Estoque (kg)' : 'Estoque' }}</label>
              <input v-model="form.stock_quantity" type="number" :step="form.unit === 'KG' ? 0.001 : 1" min="0" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Estoque Mínimo</label>
              <input v-model="form.min_stock" type="number" min="0" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Unidade</label>
            <select v-model="form.unit"
                    class="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <option value="UN">Unidade</option>
              <option value="KG">Quilograma (kg)</option>
            </select>
          </div>

          <div class="mb-4">
            <label class="flex items-center">
              <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
              <span class="ml-2 text-sm text-gray-700">Ativo</span>
            </label>
          </div>

          <div class="flex justify-end space-x-3">
            <button type="button" @click="closeModal" 
                    class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" 
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors">
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Nova Categoria -->
    <div v-if="showCategoryModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeCategoryModal">
      <div class="relative top-20 mx-auto p-6 border-2 border-orange-300 w-full max-w-md shadow-2xl rounded-xl bg-white">
        <h3 class="text-xl font-bold text-blue-800 mb-4">Nova Categoria</h3>
        <form @submit.prevent="saveCategory">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input v-model="categoryForm.name" type="text" required placeholder="Ex: Rações"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Descrição (opcional)</label>
            <textarea v-model="categoryForm.description" rows="2" placeholder="Descrição da categoria"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
          </div>
          <p v-if="categoryError" class="mb-2 text-sm text-red-600">{{ categoryError }}</p>
          <div class="flex justify-end gap-3">
            <button type="button" @click="closeCategoryModal"
                    class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">
              Salvar Categoria
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { productsService } from '@/services/products'
import { useSubscriptionStore } from '@/stores/subscription'
import Pagination from '@/components/Pagination.vue'

const subscriptionStore = useSubscriptionStore()
const products = ref([])
const categories = ref([])
const showModal = ref(false)
const showCategoryModal = ref(false)
const categoryError = ref('')
const editingProduct = ref(null)
const categoryForm = ref({ name: '', description: '' })
const loading = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = ref(20)
const searchQuery = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

const imageFile = ref(null)
const imagePreviewUrl = ref(null)
const fileInputRef = ref(null)

const form = ref({
  name: '',
  description: '',
  category: '',
  sku: '',
  barcode: '',
  cost_price: 0,
  profit_margin: 0,
  sale_price: 0,
  price_manually_set: false,
  stock_quantity: 0,
  min_stock: 0,
  unit: 'UN',
  is_active: true,
})

function onImageSelect(e) {
  const file = e.target.files?.[0]
  imageFile.value = file || null
  if (imagePreviewUrl.value && imagePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  imagePreviewUrl.value = null
  if (file) {
    imagePreviewUrl.value = URL.createObjectURL(file)
  } else if (editingProduct.value?.image_url) {
    imagePreviewUrl.value = editingProduct.value.image_url
  }
}

function clearImagePreview() {
  if (imagePreviewUrl.value && imagePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  imagePreviewUrl.value = null
  imageFile.value = null
}

const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    const response = await productsService.getAll(params)
    const data = response.data
    products.value = data.results ?? data
    if (!Array.isArray(products.value)) products.value = []
    totalCount.value = data.count ?? products.value.length
  } catch (error) {
    console.error('Erro ao carregar produtos:', error)
    products.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadProducts()
  }
}

// Debounce da busca: ao digitar, volta para página 1 e recarrega após 350ms
let searchDebounce = null
watch(searchQuery, () => {
  currentPage.value = 1
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => loadProducts(), 350)
})

const loadCategories = async () => {
  try {
    const response = await productsService.getCategories()
    categories.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar categorias:', error)
  }
}

const openModal = (product = null) => {
  editingProduct.value = product
  clearImagePreview()
  if (product) {
    const unit = product.unit ?? 'UN'
    form.value = {
      name: product.name ?? '',
      description: product.description ?? '',
      category: product.category ?? '',
      sku: product.sku ?? '',
      barcode: product.barcode ?? '',
      cost_price: product.cost_price ?? 0,
      profit_margin: product.profit_margin ?? 0,
      sale_price: product.sale_price ?? 0,
      price_manually_set: product.price_manually_set ?? false,
      price_per_kg: product.price_per_kg ?? null,
      stock_quantity: unit === 'KG' ? ((product.stock_quantity ?? 0) / 1000) : (product.stock_quantity ?? 0),
      min_stock: product.min_stock ?? 0,
      unit,
      is_active: product.is_active !== false,
    }
    if (product.image_url) {
      imagePreviewUrl.value = product.image_url
    }
  } else {
    form.value = {
      name: '',
      description: '',
      category: '',
      sku: '',
      barcode: '',
      cost_price: 0,
      profit_margin: 0,
      sale_price: 0,
      price_manually_set: false,
      price_per_kg: null,
      stock_quantity: 0,
      min_stock: 0,
      unit: 'UN',
      is_active: true,
    }
  }
  showModal.value = true
  nextTick(() => {
    if (fileInputRef.value) fileInputRef.value.value = ''
  })
}

const closeModal = () => {
  showModal.value = false
  editingProduct.value = null
  clearImagePreview()
}

function openCategoryModal() {
  categoryForm.value = { name: '', description: '' }
  categoryError.value = ''
  showCategoryModal.value = true
}

function closeCategoryModal() {
  showCategoryModal.value = false
  categoryForm.value = { name: '', description: '' }
  categoryError.value = ''
}

async function saveCategory() {
  categoryError.value = ''
  try {
    const res = await productsService.createCategory({
      name: categoryForm.value.name.trim(),
      description: (categoryForm.value.description || '').trim(),
      is_active: true,
    })
    const newCat = res.data
    await loadCategories()
    if (showModal.value && newCat?.id) {
      form.value.category = newCat.id
    }
    closeCategoryModal()
  } catch (err) {
    categoryError.value = err.response?.data?.name?.[0] || err.response?.data?.detail || err.response?.data?.error || 'Erro ao salvar categoria'
  }
}

const saveProduct = async () => {
  try {
    const unit = (form.value.unit || 'UN').trim() || 'UN'
    const stockVal = parseFloat(form.value.stock_quantity) || 0
    const payload = {
      name: String(form.value.name).trim(),
      description: String(form.value.description || '').trim(),
      category: parseInt(form.value.category),
      sku: (form.value.sku || '').trim() || null,
      barcode: (form.value.barcode || '').trim() || null,
      cost_price: parseFloat(form.value.cost_price) || 0,
      profit_margin: parseFloat(form.value.profit_margin) || 0,
      sale_price: parseFloat(form.value.sale_price) || 0.01,
      price_manually_set: Boolean(form.value.price_manually_set),
      price_per_kg: unit === 'KG' ? (parseFloat(form.value.price_per_kg) || null) : null,
      stock_quantity: unit === 'KG' ? Math.round(stockVal * 1000) : Math.max(0, parseInt(stockVal) || 0),
      min_stock: parseInt(form.value.min_stock) || 0,
      unit,
      is_active: form.value.is_active !== false,
    }
    if (imageFile.value) {
      const formData = new FormData()
      Object.entries(payload).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, value === true ? 'true' : value === false ? 'false' : String(value))
        }
      })
      formData.append('image', imageFile.value)
      if (editingProduct.value) {
        await productsService.update(editingProduct.value.id, formData)
      } else {
        await productsService.create(formData)
      }
    } else {
      if (editingProduct.value) {
        await productsService.update(editingProduct.value.id, payload)
      } else {
        await productsService.create(payload)
      }
    }
    await loadProducts()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar produto:', error)
    const err = error.response?.data
    const errorMsg = err?.details || err?.error || (typeof err?.name === 'object' ? err?.name?.[0] : err?.name) || 'Erro ao salvar produto'
    alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
  }
}

const deleteProduct = async (id) => {
  if (!confirm('Deseja realmente excluir este produto?')) return
  
  try {
    await productsService.delete(id)
    await loadProducts()
  } catch (error) {
    console.error('Erro ao excluir produto:', error)
    const msg = error.response?.data?.error ?? error.response?.data?.detail ?? 'Erro ao excluir produto'
    alert(typeof msg === 'string' ? msg : JSON.stringify(msg))
  }
}

const formatPrice = (price) => {
  return parseFloat(price).toFixed(2).replace('.', ',')
}

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>