<template>
  <Teleport to="body">
    <div
      v-if="showAlert"
      role="alert"
      class="fixed bottom-14 left-0 right-0 z-[9999] px-4 py-3 shadow-2xl animate-in no-print md:bottom-16"
      :class="alertClass"
    >
      <div class="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4">
        <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded font-bold text-sm uppercase shrink-0">
          <svg class="w-5 h-5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
          {{ label }}
        </span>
        <span class="font-semibold text-center sm:text-left">
          {{ message }}
        </span>
        <router-link
          to="/admin/plan"
          class="inline-flex items-center gap-1.5 px-4 py-2 font-bold rounded-lg shadow-lg hover:opacity-90 transition-opacity text-sm shrink-0 border-2"
          :class="buttonClass"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4z" clip-rule="evenodd"/>
            <path d="M12 2a2 2 0 012 2v4a2 2 0 01-2 2V4h-2z"/>
          </svg>
          {{ buttonText }}
        </router-link>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSubscriptionStore } from '@/stores/subscription'

const authStore = useAuthStore()
const subscriptionStore = useSubscriptionStore()
const route = useRoute()
const loaded = ref(false)

const showAlert = computed(() => {
  if (!authStore.token) return false
  if (route.name !== 'Dashboard') return false
  if (loaded.value && subscriptionStore.isTrial && subscriptionStore.daysRemainingTrial > 0) return true
  if (loaded.value && subscriptionStore.isReadOnly) return true
  return false
})

const label = computed(() => {
  if (subscriptionStore.isReadOnly) return 'Atenção'
  return 'Período de teste'
})

const message = computed(() => {
  if (subscriptionStore.isReadOnly) {
    return 'Assinatura expirada. Modo leitura — você pode visualizar, mas não pode criar ou editar.'
  }
  const d = subscriptionStore.daysRemainingTrial
  return `${d} ${d === 1 ? 'dia' : 'dias'} restante${d === 1 ? '' : 's'} para ativar seu plano.`
})

const buttonText = computed(() => {
  return subscriptionStore.isReadOnly ? 'Renovar plano' : 'Ativar plano agora'
})

const alertClass = computed(() => {
  if (subscriptionStore.isReadOnly) {
    return 'bg-red-600 text-white border-t-4 border-red-800'
  }
  return 'bg-amber-500 text-amber-950 border-t-4 border-amber-700'
})

const buttonClass = computed(() => {
  if (subscriptionStore.isReadOnly) {
    return 'bg-white text-red-700 border-white hover:bg-red-50'
  }
  return 'bg-white text-amber-800 border-amber-800 hover:bg-amber-50'
})

async function loadSubscription() {
  if (!authStore.token) return
  try {
    await subscriptionStore.fetchStatus()
  } catch {}
  loaded.value = true
}

watch(() => authStore.token, (token) => {
  if (token) loadSubscription()
  else loaded.value = false
}, { immediate: true })

onMounted(() => {
  if (authStore.token) loadSubscription()
})
</script>

<style scoped>
.animate-in {
  animation: slideUp 0.3s ease-out;
}
@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
