<template>
  <div class="bg-white rounded-xl shadow-md border-2 border-orange-100 overflow-hidden p-4 sm:p-5">
    <h2 class="text-lg font-bold text-gray-800 mb-3">Insights do Dia</h2>
    <ul v-if="insights?.length" class="space-y-2">
      <li v-for="(text, i) in insights" :key="i"
          class="flex items-start gap-2 text-sm text-gray-700">
        <span class="text-orange-500 mt-0.5">•</span>
        <span>{{ text }}</span>
      </li>
    </ul>
    <p v-else class="text-gray-500 text-sm">Nenhum insight específico para hoje.</p>
  </div>
</template>

<script setup>
defineProps({
  insights: { type: Array, default: () => [] },
})
</script>
