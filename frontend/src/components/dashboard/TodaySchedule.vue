<template>
  <div class="bg-white rounded-xl shadow-md border-2 theme-card overflow-hidden">
    <div class="theme-table-header px-4 py-3 sm:px-6 sm:py-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-white mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h2 class="text-lg sm:text-xl font-bold text-white">Agenda do Dia</h2>
        </div>
        <div class="flex items-center gap-2">
          <span class="bg-white text-orange-600 px-3 py-1 rounded-full text-sm font-semibold">
            {{ schedule?.length ?? 0 }} agendamento(s)
          </span>
          <router-link to="/scheduling" class="px-3 py-1.5 bg-white text-orange-600 rounded-lg text-sm font-semibold hover:bg-orange-50 transition-colors">
            Novo
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="loading" class="p-8 text-center text-gray-500">Carregando...</div>

    <div v-else-if="!schedule?.length" class="p-8 text-center">
      <p class="text-gray-500">Nenhum agendamento para hoje</p>
      <router-link to="/scheduling" class="mt-3 inline-block text-orange-600 font-medium hover:underline">
        Agendar
      </router-link>
    </div>

    <div v-else class="divide-y divide-gray-200 max-h-[400px] overflow-y-auto">
      <div
        v-for="apt in schedule"
        :key="apt.id"
        class="p-4 sm:p-5 hover:bg-orange-50 transition-colors flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
      >
        <div class="flex items-start gap-3 flex-1">
          <div :class="['flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold', statusClass(apt.status)]">
            {{ apt.time }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-1">
              <span class="font-semibold text-gray-900">{{ apt.client }}</span>
              <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', statusBadgeClass(apt.status)]">
                {{ apt.status_display }}
              </span>
            </div>
            <p class="text-sm text-gray-600">{{ apt.pet }} - {{ apt.service }}</p>
          </div>
        </div>
        <div class="flex gap-2 flex-shrink-0">
          <button
            v-if="['scheduled','confirmed','in_progress'].includes(apt.status)"
            @click="$emit('complete', apt.id)"
            class="px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
          >
            Concluir
          </button>
          <button
            v-if="!['cancelled','completed','done'].includes(apt.status)"
            @click="$emit('cancel', apt.id)"
            class="px-3 py-1.5 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700"
          >
            Cancelar
          </button>
          <router-link :to="{ path: '/scheduling', query: { edit: apt.id } }"
                      class="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-300">
            Ver
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  schedule: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

defineEmits(['complete', 'cancel'])

function statusClass(status) {
  const m = { scheduled: 'bg-blue-500', confirmed: 'bg-blue-500', in_progress: 'bg-amber-500', completed: 'bg-green-600', done: 'bg-green-600', cancelled: 'bg-gray-400', no_show: 'bg-gray-400' }
  return m[status] || 'bg-gray-400'
}

function statusBadgeClass(status) {
  const m = { scheduled: 'bg-blue-100 text-blue-800', confirmed: 'bg-blue-100 text-blue-800', in_progress: 'bg-amber-100 text-amber-800', completed: 'bg-green-100 text-green-800', done: 'bg-green-100 text-green-800', cancelled: 'bg-gray-100 text-gray-800', no_show: 'bg-gray-100 text-gray-800' }
  return m[status] || 'bg-gray-100 text-gray-800'
}
</script>
