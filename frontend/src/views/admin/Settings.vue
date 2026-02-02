<template>
  <div>
    <div class="flex items-center mb-6">
      <svg class="w-7 h-7 text-orange-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
        <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
      </svg>
      <h1 class="text-2xl font-bold text-gray-800">Configurações do Sistema</h1>
    </div>

    <!-- Horário de Funcionamento -->
    <div class="bg-white rounded-lg shadow border-2 border-orange-200 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Horário de Funcionamento</h2>
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Intervalo do slot (min)</label>
            <input v-model.number="config.slot_minutes" type="number" min="15" max="120" step="15"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fuso horário</label>
            <input v-model="config.timezone" type="text" placeholder="America/Fortaleza"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg">
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-100">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">Dia</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">Aberto</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">Abertura</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">Fechamento</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">Pausa Início</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">Pausa Fim</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="(r, idx) in config.rules" :key="idx" class="hover:bg-gray-50">
                <td class="px-4 py-2 font-medium text-gray-800">{{ weekdays[r.weekday] }}</td>
                <td class="px-4 py-2">
                  <input v-model="r.is_open" type="checkbox" class="rounded border-gray-300 text-orange-500">
                </td>
                <td class="px-4 py-2">
                  <input v-model="r.open_time" type="time" class="px-2 py-1 border border-gray-300 rounded"
                         :disabled="!r.is_open">
                </td>
                <td class="px-4 py-2">
                  <input v-model="r.close_time" type="time" class="px-2 py-1 border border-gray-300 rounded"
                         :disabled="!r.is_open">
                </td>
                <td class="px-4 py-2">
                  <input v-model="r.break_start" type="time" class="px-2 py-1 border border-gray-300 rounded w-24"
                         :disabled="!r.is_open">
                </td>
                <td class="px-4 py-2">
                  <input v-model="r.break_end" type="time" class="px-2 py-1 border border-gray-300 rounded w-24"
                         :disabled="!r.is_open">
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <button @click="saveBusinessHours" :disabled="saving"
                class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50">
          {{ saving ? 'Salvando...' : 'Salvar horários' }}
        </button>
      </div>
    </div>

    <!-- Fechamentos (feriados/folgas) -->
    <div class="bg-white rounded-lg shadow border-2 border-orange-200 p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Datas de Fechamento</h2>
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="newClosure.date" type="date" class="px-3 py-2 border border-gray-300 rounded-lg">
        <input v-model="newClosure.reason" type="text" placeholder="Motivo (ex: Natal)" maxlength="100"
               class="px-3 py-2 border border-gray-300 rounded-lg flex-1 min-w-[150px]">
        <button @click="addClosure" :disabled="!newClosure.date"
                class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50">
          Adicionar
        </button>
      </div>
      <ul class="divide-y divide-gray-200">
        <li v-for="c in closures" :key="c.id" class="flex justify-between items-center py-2">
          <span>{{ formatDate(c.date) }} – {{ c.reason || 'Fechado' }}</span>
          <button @click="deleteClosure(c.id)" class="text-red-600 hover:text-red-800 text-sm">Remover</button>
        </li>
        <li v-if="closures.length === 0" class="py-4 text-gray-500 text-sm">Nenhuma data de fechamento cadastrada</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { settingsService } from '@/services/settings'

const saving = ref(false)
const config = ref({
  slot_minutes: 30,
  timezone: 'America/Fortaleza',
  rules: [
    { weekday: 0, is_open: true, open_time: '08:00', close_time: '18:00', break_start: '', break_end: '' },
    { weekday: 1, is_open: true, open_time: '08:00', close_time: '18:00', break_start: '', break_end: '' },
    { weekday: 2, is_open: true, open_time: '08:00', close_time: '18:00', break_start: '', break_end: '' },
    { weekday: 3, is_open: true, open_time: '08:00', close_time: '18:00', break_start: '', break_end: '' },
    { weekday: 4, is_open: true, open_time: '08:00', close_time: '18:00', break_start: '', break_end: '' },
    { weekday: 5, is_open: true, open_time: '08:00', close_time: '18:00', break_start: '', break_end: '' },
    { weekday: 6, is_open: false, open_time: '', close_time: '', break_start: '', break_end: '' },
  ],
})
const weekdays = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
const closures = ref([])
const newClosure = ref({ date: '', reason: '' })

function normalizeTime(v) {
  if (!v || typeof v !== 'string') return ''
  if (v.length === 5 && v.includes(':')) return v
  return ''
}

async function loadBusinessHours() {
  try {
    const res = await settingsService.getBusinessHours()
    const d = res.data
    config.value.slot_minutes = d.slot_minutes ?? 30
    config.value.timezone = d.timezone ?? 'America/Fortaleza'
    if (d.rules && d.rules.length) {
      config.value.rules = d.rules.map(r => ({
        weekday: r.weekday,
        is_open: r.is_open ?? true,
        open_time: normalizeTime(r.open_time_str || r.open_time) || (r.is_open ? '08:00' : ''),
        close_time: normalizeTime(r.close_time_str || r.close_time) || (r.is_open ? '18:00' : ''),
        break_start: normalizeTime(r.break_start_str || r.break_start) || '',
        break_end: normalizeTime(r.break_end_str || r.break_end) || '',
      }))
    }
  } catch {
    config.value.rules = weekdays.map((_, i) => ({
      weekday: i,
      is_open: i < 6,
      open_time: i < 6 ? '08:00' : '',
      close_time: i < 6 ? '18:00' : '',
      break_start: '',
      break_end: '',
    }))
  }
}

async function saveBusinessHours() {
  saving.value = true
  try {
    const payload = {
      slot_minutes: config.value.slot_minutes,
      timezone: config.value.timezone,
      rules: config.value.rules.map(r => ({
        weekday: r.weekday,
        is_open: r.is_open,
        open_time: r.open_time || null,
        close_time: r.close_time || null,
        break_start: r.break_start || null,
        break_end: r.break_end || null,
      })),
    }
    await settingsService.updateBusinessHours(payload)
    alert('Horários salvos com sucesso!')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar.')
  } finally {
    saving.value = false
  }
}

async function loadClosures() {
  try {
    const res = await settingsService.getClosures()
    closures.value = res.data
  } catch {
    closures.value = []
  }
}

async function addClosure() {
  if (!newClosure.value.date) return
  try {
    await settingsService.addClosure({ date: newClosure.value.date, reason: newClosure.value.reason })
    newClosure.value = { date: '', reason: '' }
    await loadClosures()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao adicionar.')
  }
}

async function deleteClosure(id) {
  if (!confirm('Remover esta data de fechamento?')) return
  try {
    await settingsService.deleteClosure(id)
    await loadClosures()
  } catch {
    alert('Erro ao remover.')
  }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR')
}

onMounted(() => {
  loadBusinessHours()
  loadClosures()
})
</script>
