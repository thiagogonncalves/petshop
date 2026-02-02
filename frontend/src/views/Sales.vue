<template>
  <div>
    <div class="flex items-center mb-6">
      <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
      </svg>
      <h1 class="text-2xl font-bold text-blue-800">Vendas realizadas</h1>
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
              <button @click="openReceipt(sale.id)" class="text-blue-600 hover:text-blue-900">Recibo</button>
            </td>
          </tr>
          <tr v-if="sales.length === 0">
            <td colspan="7" class="px-6 py-4 text-center text-sm text-gray-500">Nenhuma venda encontrada</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { salesService } from '@/services/sales'

const router = useRouter()
const sales = ref([])

const loadSales = async () => {
  try {
    const response = await salesService.getAll()
    sales.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar vendas:', error)
    alert('Erro ao carregar vendas')
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

const openReceipt = (saleId) => {
  router.push({ name: 'ReceiptPrint', params: { id: String(saleId) } })
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
})
</script>