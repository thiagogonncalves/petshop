<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Vendas</h1>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors"
      >
        Nova Venda
      </button>
    </div>

    <!-- Tabela de Vendas -->
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Cliente</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Data</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Total</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Pagamento</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="sale in sales" :key="sale.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ sale.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ sale.client_name || 'Venda Avulsa' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(sale.sale_date) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">R$ {{ formatPrice(sale.total) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ sale.payment_method_display }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusColor(sale.status)" 
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ sale.status_display }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button v-if="sale.status === 'pending'" @click="completePayment(sale.id)" 
                      class="text-green-600 hover:text-green-900 mr-4">Pagar</button>
              <button @click="viewSale(sale)" class="text-blue-600 hover:text-blue-900 mr-4">Ver</button>
              <button @click="generateReceipt(sale.id)" class="text-blue-600 hover:text-blue-900">Recibo</button>
            </td>
          </tr>
          <tr v-if="sales.length === 0">
            <td colspan="7" class="px-6 py-4 text-center text-sm text-gray-500">Nenhuma venda encontrada</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal de Venda -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeModal">
      <div class="relative top-10 mx-auto p-6 border-2 border-orange-300 w-full max-w-4xl shadow-2xl rounded-xl bg-white max-h-[90vh] overflow-y-auto">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">Nova Venda</h3>
        </div>
        
        <form @submit.prevent="saveSale">
          <div class="mb-4">
            <div class="flex items-center justify-between mb-2">
              <label class="block text-sm font-medium text-gray-700">Cliente</label>
              <div class="flex items-center space-x-2">
                <label class="flex items-center">
                  <input v-model="form.is_generic_sale" type="checkbox" @change="form.client = ''" 
                         class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                  <span class="ml-2 text-sm text-gray-600">Venda Avulsa</span>
                </label>
                <button type="button" @click="showClientModal = true" 
                        class="text-sm text-blue-600 hover:text-blue-800">+ Novo Cliente</button>
              </div>
            </div>
            <select v-model="form.client" :required="!form.is_generic_sale"
                    :disabled="form.is_generic_sale"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100">
              <option value="">Selecione...</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">{{ client.name }}</option>
            </select>
          </div>

          <!-- Itens -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Itens</label>
            <div v-for="(item, index) in form.items" :key="index" class="border rounded p-3 mb-2">
              <div class="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2">
                <select v-model="item.item_type" @change="item.product = null; item.service = null; item.unit_price = 0; item.product_code = ''"
                        class="px-3 py-2 border border-gray-300 rounded-md">
                  <option value="product">Produto</option>
                  <option value="service">Serviço</option>
                </select>
                <div v-if="item.item_type === 'product'" class="md:col-span-2">
                  <div class="flex gap-2">
                    <input v-model="item.product_code" @keyup.enter="searchProductByCode(item)" 
                           type="text" placeholder="Código do produto"
                           class="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm">
                    <button type="button" @click="searchProductByCode(item)" 
                            class="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm transition-colors">
                      Buscar
                    </button>
                  </div>
                </div>
                <select v-if="item.item_type === 'product'" v-model="item.product" @change="updateItemPrice(item)" required
                        class="px-3 py-2 border border-gray-300 rounded-md md:col-span-1">
                  <option value="">Produto...</option>
                  <option v-for="p in products" :key="p.id" :value="p.id">
                    {{ p.sku ? `[${p.sku}] ` : '' }}{{ p.name }} - R$ {{ formatPrice(p.sale_price) }}
                  </option>
                </select>
                <select v-if="item.item_type === 'service'" v-model="item.service" @change="updateItemPrice(item)" required
                        class="px-3 py-2 border border-gray-300 rounded-md md:col-span-3">
                  <option value="">Serviço...</option>
                  <option v-for="s in services" :key="s.id" :value="s.id">{{ s.name }} - R$ {{ formatPrice(s.price) }}</option>
                </select>
              </div>
              <div class="grid grid-cols-3 gap-2">
                <input v-model.number="item.quantity" type="number" min="1" placeholder="Qtd" required
                       class="px-3 py-2 border border-gray-300 rounded-md">
                <input v-model.number="item.unit_price" type="number" step="0.01" min="0" placeholder="Preço unitário" required
                       class="px-3 py-2 border border-gray-300 rounded-md">
                <button type="button" @click="removeItem(index)" class="text-red-600 hover:text-red-800">Remover</button>
              </div>
            </div>
            <button type="button" @click="addItem" class="text-blue-600 hover:text-blue-800 text-sm font-medium">+ Adicionar Item</button>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Desconto</label>
            <input v-model="form.discount" type="number" step="0.01" min="0"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md">
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Forma de Pagamento</label>
            <select v-model="form.payment_method" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md">
              <option value="cash">Dinheiro</option>
              <option value="credit_card">Cartão de Crédito</option>
              <option value="debit_card">Cartão de Débito</option>
              <option value="pix">PIX</option>
              <option value="bank_transfer">Transferência Bancária</option>
            </select>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Total: R$ {{ calculateTotal() }}</label>
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

    <!-- Modal de Cliente Rápido -->
    <div v-if="showClientModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="showClientModal = false">
      <div class="relative top-20 mx-auto p-6 border-2 border-orange-300 w-full max-w-md shadow-2xl rounded-xl bg-white">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <h3 class="text-xl font-bold text-blue-800">Cadastrar Cliente Rápido</h3>
        </div>
        
        <form @submit.prevent="saveNewClient">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="newClientForm.name" type="text" required
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Documento</label>
            <select v-model="newClientForm.document_type"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              <option value="cpf">CPF</option>
              <option value="cnpj">CNPJ</option>
            </select>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">CPF/CNPJ</label>
            <input v-model="newClientForm.document" type="text"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefone *</label>
            <input v-model="newClientForm.phone" type="text" required
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <input v-model="newClientForm.email" type="email"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
          </div>

          <div class="flex justify-end space-x-3">
            <button type="button" @click="showClientModal = false" 
                    class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" 
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors">
              Salvar e Usar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { salesService } from '@/services/sales'
import { clientsService } from '@/services/clients'
import { productsService } from '@/services/products'
import { servicesService } from '@/services/services'

const sales = ref([])
const clients = ref([])
const products = ref([])
const services = ref([])
const showModal = ref(false)

const form = ref({
  client: '',
  is_generic_sale: false,
  items: [],
  discount: 0,
  payment_method: 'pix',
  status: 'pending',
})

const showClientModal = ref(false)
const newClientForm = ref({
  name: '',
  document_type: 'cpf',
  document: '',
  phone: '',
  email: '',
})

const loadSales = async () => {
  try {
    const response = await salesService.getAll()
    sales.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar vendas:', error)
    alert('Erro ao carregar vendas')
  }
}

const loadClients = async () => {
  try {
    const response = await clientsService.getAll({ is_active: true })
    clients.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar clientes:', error)
  }
}

const loadProducts = async () => {
  try {
    const response = await productsService.getAll({ is_active: true })
    products.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar produtos:', error)
  }
}

const loadServices = async () => {
  try {
    const response = await servicesService.getAll({ is_active: true })
    services.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar serviços:', error)
  }
}

const addItem = () => {
  form.value.items.push({
    item_type: 'product',
    product: null,
    service: null,
    product_code: '',
    quantity: 1,
    unit_price: 0,
  })
}

const searchProductByCode = (item) => {
  if (!item.product_code) return
  
  const product = products.value.find(p => 
    p.sku?.toLowerCase() === item.product_code.toLowerCase() || 
    p.barcode === item.product_code
  )
  
  if (product) {
    item.product = product.id
    updateItemPrice(item)
  } else {
    alert('Produto não encontrado com este código')
  }
}

const saveNewClient = async () => {
  try {
    const client = await clientsService.create(newClientForm.value)
    await loadClients()
    form.value.client = client.data.id
    showClientModal.value = false
    newClientForm.value = {
      name: '',
      document_type: 'cpf',
      document: '',
      phone: '',
      email: '',
    }
  } catch (error) {
    console.error('Erro ao criar cliente:', error)
    alert('Erro ao criar cliente')
  }
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const updateItemPrice = (item) => {
  if (item.item_type === 'product' && item.product) {
    const product = products.value.find(p => p.id == item.product)
    if (product) {
      item.unit_price = parseFloat(product.sale_price)
    }
  } else if (item.item_type === 'service' && item.service) {
    const service = services.value.find(s => s.id == item.service)
    if (service) {
      item.unit_price = parseFloat(service.price)
    }
  } else {
    item.unit_price = 0
  }
}

const calculateTotal = () => {
  let subtotal = form.value.items.reduce((sum, item) => {
    return sum + (parseFloat(item.unit_price || 0) * parseInt(item.quantity || 0))
  }, 0)
  const total = subtotal - parseFloat(form.value.discount || 0)
  return total.toFixed(2).replace('.', ',')
}

const openModal = () => {
  form.value = {
    client: '',
    is_generic_sale: false,
    items: [{ item_type: 'product', product: null, service: null, product_code: '', quantity: 1, unit_price: 0 }],
    discount: 0,
    payment_method: 'pix',
    status: 'pending',
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveSale = async () => {
  try {
    // Validar se tem cliente ou é venda avulsa
    if (!form.value.is_generic_sale && !form.value.client) {
      alert('Selecione um cliente ou marque como Venda Avulsa')
      return
    }
    
    // Preparar dados no formato esperado pela API
    const saleData = {
      client: form.value.is_generic_sale ? null : form.value.client,
      items: form.value.items.map(item => ({
        item_type: item.item_type,
        product: item.item_type === 'product' ? item.product : null,
        service: item.item_type === 'service' ? item.service : null,
        quantity: parseInt(item.quantity),
        unit_price: parseFloat(item.unit_price),
      })),
      discount: parseFloat(form.value.discount || 0),
      payment_method: form.value.payment_method,
      status: form.value.status,
    }
    
    await salesService.create(saleData)
    await loadSales()
    closeModal()
    alert('Venda criada com sucesso!')
  } catch (error) {
    console.error('Erro ao salvar venda:', error)
    alert('Erro ao salvar venda: ' + (error.response?.data?.details || error.message))
  }
}

const completePayment = async (id) => {
  try {
    await salesService.completePayment(id)
    await loadSales()
    alert('Pagamento realizado com sucesso!')
  } catch (error) {
    console.error('Erro ao completar pagamento:', error)
    alert('Erro ao completar pagamento')
  }
}

const viewSale = (sale) => {
  alert(`Venda #${sale.id}\nCliente: ${sale.client_name}\nTotal: R$ ${formatPrice(sale.total)}`)
}

const generateReceipt = async (id) => {
  try {
    await salesService.generateReceipt(id)
    alert('Recibo gerado com sucesso!')
  } catch (error) {
    console.error('Erro ao gerar recibo:', error)
    alert('Erro ao gerar recibo')
  }
}

const formatPrice = (price) => {
  return parseFloat(price).toFixed(2).replace('.', ',')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR')
}

const getStatusColor = (status) => {
  const colors = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'paid': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800',
    'refunded': 'bg-gray-100 text-gray-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  loadSales()
  loadClients()
  loadProducts()
  loadServices()
})
</script>