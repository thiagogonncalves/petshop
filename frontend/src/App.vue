<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useCompanyStore } from '@/stores/company'

onMounted(() => {
  useCompanyStore().fetchCompany()
})
</script>
