<template>
  <div class="fixed bottom-20 sm:bottom-6 right-4 sm:right-6 flex flex-col gap-2 z-40">
    <router-link
      v-for="action in actions"
      :key="action.path"
      :to="action.path"
      class="flex items-center gap-2 px-4 py-3 bg-orange-500 text-white rounded-xl shadow-lg hover:bg-orange-600 active:bg-orange-700 transition-colors font-medium text-sm touch-manipulation min-h-[44px]"
    >
      <span class="text-lg">{{ action.icon }}</span>
      <span>{{ action.label }}</span>
    </router-link>
  </div>
</template>

<script setup>
const actions = [
  { icon: '➕', label: 'Novo Agendamento', path: '/scheduling' },
  { icon: '🐾', label: 'Novo Cliente', path: '/clients' },
  { icon: '📦', label: 'Importar NF-e', path: '/nfe' },
]
</script>
