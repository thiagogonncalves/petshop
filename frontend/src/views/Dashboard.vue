<template>
  <div class="min-h-screen flex flex-col">
    <SubscriptionAlert />
    <div class="max-w-7xl mx-auto px-4 sm:px-6 flex-1 w-full pb-4">
      <div v-if="loading" class="grid gap-6">
        <div class="h-64 bg-gray-200 rounded-xl animate-pulse"></div>
        <div class="h-32 bg-gray-200 rounded-xl animate-pulse"></div>
      </div>

      <div v-else class="space-y-6">
        <TodaySchedule
          :schedule="data?.today_schedule ?? []"
          :loading="false"
          @complete="handleComplete"
          @cancel="handleCancel"
        />
        <DailyInsights :insights="data?.insights ?? []" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dashboardService } from '@/services/dashboard'
import { schedulingService } from '@/services/scheduling'
import TodaySchedule from '@/components/dashboard/TodaySchedule.vue'
import DailyInsights from '@/components/dashboard/DailyInsights.vue'
import SubscriptionAlert from '@/components/SubscriptionAlert.vue'

const data = ref(null)
const loading = ref(true)

async function loadDashboard() {
  loading.value = true
  try {
    const res = await dashboardService.getDashboardSummary({
      date: new Date().toISOString().slice(0, 10),
    })
    data.value = res.data
  } catch (err) {
    console.error('Erro ao carregar dashboard:', err)
    data.value = { today_schedule: [], insights: [] }
  } finally {
    loading.value = false
  }
}

async function handleComplete(id) {
  if (!confirm('Marcar agendamento como concluído?')) return
  try {
    await schedulingService.complete(id)
    await loadDashboard()
  } catch (err) {
    console.error(err)
    alert('Erro ao concluir agendamento')
  }
}

async function handleCancel(id) {
  if (!confirm('Cancelar este agendamento?')) return
  try {
    await schedulingService.cancel(id)
    await loadDashboard()
  } catch (err) {
    console.error(err)
    alert('Erro ao cancelar agendamento')
  }
}

onMounted(() => {
  loadDashboard()
})
</script>
