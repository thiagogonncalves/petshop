<template>
  <div class="receipt-root">
    <div v-if="loading" class="p-4 text-center text-gray-600">Carregando cupom...</div>
    <div v-else-if="error" class="p-4 text-center text-red-600">{{ error }}</div>
    <div v-else ref="receiptRef" class="receipt-paper">
      <div class="receipt-header">
        <h1 class="receipt-title">{{ company.name || 'GB PET' }}</h1>
        <p v-if="company.cpf_cnpj" class="receipt-cpf">{{ company.cpf_cnpj }}</p>
        <p v-if="company.address" class="receipt-address">{{ company.address }}{{ company.address_number ? ', ' + company.address_number : '' }}</p>
        <p class="receipt-subtitle">Cupom Fiscal / Comprovante</p>
      </div>
      <div class="receipt-meta">
        <p>Venda #{{ receipt.sale_id }}</p>
        <p>{{ formatDate(receipt.sale_date) }}</p>
      </div>
      <hr class="receipt-hr" />
      <div class="receipt-items">
        <div v-for="(item, i) in receipt.items" :key="i" class="receipt-item">
          <p class="item-name">{{ item.name }}</p>
          <p class="item-line">{{ item.quantity }} x R$ {{ item.unit_price }} = R$ {{ item.total }}</p>
        </div>
      </div>
      <hr class="receipt-hr" />
      <div class="receipt-totals">
        <p v-if="receipt.discount && receipt.discount !== '0.00'">Subtotal: R$ {{ receipt.subtotal }}</p>
        <p v-if="receipt.discount && receipt.discount !== '0.00'">Desconto: R$ {{ receipt.discount }}</p>
        <p class="receipt-total">TOTAL: R$ {{ receipt.total }}</p>
      </div>
      <hr class="receipt-hr" />
      <div class="receipt-client">
        <p>{{ receipt.client }}</p>
        <p>Pagamento: {{ receipt.payment_method }}</p>
      </div>
      <div class="receipt-footer">
        <p>Obrigado pela preferência!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { salesService } from '@/services/sales'
import { companyService } from '@/services/company'

const route = useRoute()
const company = ref({})
const receipt = ref({
  sale_id: null,
  sale_date: null,
  items: [],
  subtotal: '0.00',
  discount: '0.00',
  total: '0.00',
  client: 'Venda avulsa',
  payment_method: '-',
})
const loading = ref(true)
const error = ref('')
const receiptRef = ref(null)

function formatDate(iso) {
  if (!iso) return '-'
  try {
    const d = new Date(iso)
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function loadReceipt(id) {
  if (!id) return
  loading.value = true
  error.value = ''
  salesService.getReceipt(id).then(({ data }) => {
    receipt.value = {
      sale_id: data.sale_id,
      sale_date: data.sale_date,
      items: data.items || [],
      subtotal: data.subtotal || '0.00',
      discount: data.discount || '0.00',
      total: data.total || '0.00',
      client: data.client || 'Venda avulsa',
      payment_method: data.payment_method || '-',
    }
    loading.value = false
    setTimeout(() => {
      window.print()
    }, 300)
  }).catch((err) => {
    error.value = err.response?.data?.detail || 'Erro ao carregar cupom'
    loading.value = false
  })
}

onMounted(async () => {
  try {
    const { data } = await companyService.get()
    company.value = data || {}
  } catch {
    company.value = {}
  }
  const id = route.params.id
  loadReceipt(id)
})

watch(() => route.params.id, (id) => {
  loadReceipt(id)
})
</script>

<style scoped>
.receipt-root {
  padding: 1rem;
  background: #f3f4f6;
  min-height: 100vh;
}

.receipt-paper {
  width: 80mm;
  max-width: 80mm;
  margin: 0 auto;
  padding: 8px;
  background: white;
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  line-height: 1.35;
  color: #000;
  word-break: break-word;
}

.receipt-header {
  text-align: center;
  margin-bottom: 8px;
}

.receipt-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0;
}

.receipt-cpf,
.receipt-address {
  font-size: 10px;
  margin: 2px 0 0 0;
  color: #444;
}

.receipt-subtitle {
  font-size: 11px;
  margin: 2px 0 0 0;
  color: #444;
}

.receipt-meta {
  text-align: center;
  font-size: 11px;
  margin-bottom: 6px;
}

.receipt-meta p {
  margin: 2px 0;
}

.receipt-hr {
  border: none;
  border-top: 1px dashed #999;
  margin: 6px 0;
}

.receipt-items {
  margin: 6px 0;
}

.receipt-item {
  margin-bottom: 6px;
}

.item-name {
  margin: 0;
  font-weight: 500;
  white-space: normal;
  word-wrap: break-word;
}

.item-line {
  margin: 2px 0 0 0;
  font-size: 11px;
  color: #333;
}

.receipt-totals {
  text-align: right;
  margin: 6px 0;
}

.receipt-totals p {
  margin: 2px 0;
}

.receipt-total {
  font-size: 14px;
  font-weight: bold;
}

.receipt-client {
  font-size: 11px;
  margin: 6px 0;
}

.receipt-client p {
  margin: 2px 0;
}

.receipt-footer {
  text-align: center;
  margin-top: 12px;
  font-size: 11px;
}

@media print {
  /* Imprime só o cupom: esconde carregando, erro e fundo da página */
  .receipt-root {
    padding: 0;
    margin: 0;
    background: white;
    min-height: auto;
  }

  .receipt-root > *:not(.receipt-paper) {
    display: none !important;
  }

  .receipt-paper {
    box-shadow: none;
    margin: 0;
    padding: 8px;
  }

  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>
