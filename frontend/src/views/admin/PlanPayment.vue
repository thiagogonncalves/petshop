<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Plano e Pagamento</h1>

    <div v-if="loading" class="bg-white rounded-xl shadow p-8 text-center text-gray-500">
      Carregando...
    </div>

    <div v-else class="space-y-6">
      <!-- Status atual -->
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Status atual</h2>
        <div class="flex items-center gap-2">
          <span
            class="inline-flex px-3 py-1 rounded-full text-sm font-medium"
            :class="statusBadgeClass"
          >
            {{ statusLabel }}
          </span>
        </div>
        <p v-if="subscription.trialEnd" class="mt-2 text-sm text-gray-600">
          <template v-if="subscription.status === 'trial' && subscription.daysRemainingTrial > 0">
            {{ subscription.daysRemainingTrial }} dia(s) restante(s) no período de teste.
          </template>
          <template v-else-if="subscription.currentPeriodEnd">
            Válido até {{ formatDate(subscription.currentPeriodEnd) }}
          </template>
        </p>
      </div>

      <!-- Plano e valor -->
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Plano</h2>
        <div v-if="subscription.plan" class="flex justify-between items-center">
          <div>
            <p class="font-medium text-gray-800">{{ subscription.plan.name }}</p>
            <p class="text-2xl font-bold text-orange-600 mt-1">
              R$ {{ subscription.plan.price }}/mês
            </p>
          </div>
          <button
            v-if="!subscription.canWrite || subscription.status === 'trial'"
            type="button"
            :disabled="payLoading"
            class="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
            @click="handleActivate"
          >
            {{ payLoading ? 'Gerando...' : 'Ativar plano' }}
          </button>
        </div>
        <p v-else class="text-gray-600">Nenhum plano configurado.</p>
      </div>

      <!-- Aviso modo leitura -->
      <div
        v-if="!subscription.canWrite"
        class="bg-amber-50 border border-amber-200 rounded-xl p-4"
      >
        <p class="text-amber-800 font-medium">Modo leitura</p>
        <p class="text-amber-700 text-sm mt-1">
          Sua assinatura expirou. Você pode visualizar todos os dados, mas não pode criar ou editar.
          Ative o plano para continuar usando o sistema normalmente.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSubscriptionStore } from '@/stores/subscription'

const subStore = useSubscriptionStore()
const loading = ref(true)
const payLoading = ref(false)

const subscription = computed(() => ({
  status: subStore.status,
  canWrite: subStore.canWrite,
  daysRemainingTrial: subStore.daysRemainingTrial,
  trialEnd: subStore.trialEnd,
  plan: subStore.plan,
  currentPeriodEnd: subStore.currentPeriodEnd,
}))

const statusLabel = computed(() => {
  const s = subStore.status
  if (s === 'trial') return 'Período de teste'
  if (s === 'active') return 'Ativo'
  if (s === 'expired') return 'Expirado'
  if (s === 'cancelled') return 'Cancelado'
  return s
})

const statusBadgeClass = computed(() => {
  const s = subStore.status
  if (s === 'active') return 'bg-green-100 text-green-800'
  if (s === 'trial') return 'bg-blue-100 text-blue-800'
  if (s === 'expired') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
})

function formatDate(iso) {
  if (!iso) return '-'
  try {
    return new Date(iso).toLocaleDateString('pt-BR')
  } catch {
    return iso
  }
}

async function handleActivate() {
  payLoading.value = true
  try {
    const data = await subStore.createPayment()
    if (data?.init_point) {
      window.location.href = data.init_point
    }
  } catch (err) {
    const d = err.response?.data
    const msg = d?.detail || d?.details?.detail || d?.message || 'Erro ao gerar pagamento'
    alert(typeof msg === 'string' ? msg : JSON.stringify(msg))
  } finally {
    payLoading.value = false
  }
}

onMounted(async () => {
  try {
    await subStore.fetchStatus()
  } catch {
    // Ignorar erro - status pode estar em cache
  } finally {
    loading.value = false
  }
})
</script>
