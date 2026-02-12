<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z" />
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Módulo Fiscal</h1>
      </div>
    </div>
    <div class="flex gap-2 mb-4">
      <router-link
        to="/fiscal/nfe"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        :class="isNFeActive ? 'theme-accent theme-accent-text' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
      >
        NF-e
      </router-link>
      <router-link
        v-if="authStore.isAdmin"
        to="/fiscal/config"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        :class="isConfigActive ? 'theme-accent theme-accent-text' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
      >
        Configuração SEFAZ
      </router-link>
    </div>
    <RouterView />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const isNFeActive = computed(() => route.path.startsWith('/fiscal/nfe'))
const isConfigActive = computed(() => route.path === '/fiscal/config')
</script>
