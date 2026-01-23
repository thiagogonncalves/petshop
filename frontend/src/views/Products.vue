<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Produtos</h1>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors"
      >
        Novo Produto
      </button>
    </div>

    <!-- Tabela de Produtos -->
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Código</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Categoria</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Preço</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Estoque</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="product in products" :key="product.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ product.sku || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ product.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ product.category_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">R$ {{ formatPrice(product.sale_price) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span :class="product.is_low_stock ? 'text-red-600 font-semibold' : 'text-gray-500'">
                {{ product.stock_quantity }} {{ product.unit }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" 
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ product.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="openModal(product)" class="text-blue-600 hover:text-blue-800 mr-4">Editar</button>
              <button @click="deleteProduct(product.id)" class="text-red-600 hover:text-red-900">Excluir</button>
            </td>
          </tr>
          <tr v-if="products.length === 0">
            <td colspan="8" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum produto encontrado</td>
          </tr>
        </tbody>
      </table>
    </div>

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
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input v-model="form.name" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
              <select v-model="form.category" required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="">Selecione...</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço de Venda</label>
              <input v-model="form.sale_price" type="number" step="0.01" min="0" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Estoque</label>
              <input v-model="form.stock_quantity" type="number" min="0" required
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
            <input v-model="form.unit" type="text" placeholder="Ex: un, kg, litro"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { productsService } from '@/services/products'

const products = ref([])
const categories = ref([])
const showModal = ref(false)
const editingProduct = ref(null)

const form = ref({
  name: '',
  category: '',
  cost_price: 0,
  sale_price: 0,
  stock_quantity: 0,
  min_stock: 0,
  unit: 'un',
  is_active: true,
})

const loadProducts = async () => {
  try {
    const response = await productsService.getAll()
    products.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar produtos:', error)
    alert('Erro ao carregar produtos')
  }
}

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
  if (product) {
    form.value = { ...product }
  } else {
    form.value = {
      name: '',
      category: '',
      cost_price: 0,
      sale_price: 0,
      stock_quantity: 0,
      min_stock: 0,
      unit: 'un',
      is_active: true,
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingProduct.value = null
}

const saveProduct = async () => {
  try {
    const data = {
      ...form.value,
      category: parseInt(form.value.category),
      cost_price: parseFloat(form.value.cost_price),
      sale_price: parseFloat(form.value.sale_price),
      stock_quantity: parseInt(form.value.stock_quantity),
      min_stock: parseInt(form.value.min_stock),
    }
    
    if (editingProduct.value) {
      await productsService.update(editingProduct.value.id, data)
    } else {
      await productsService.create(data)
    }
    await loadProducts()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar produto:', error)
    const errorMsg = error.response?.data?.details || error.response?.data?.error || 'Erro ao salvar produto'
    alert(errorMsg)
  }
}

const deleteProduct = async (id) => {
  if (!confirm('Deseja realmente excluir este produto?')) return
  
  try {
    await productsService.delete(id)
    await loadProducts()
  } catch (error) {
    console.error('Erro ao excluir produto:', error)
    alert('Erro ao excluir produto')
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