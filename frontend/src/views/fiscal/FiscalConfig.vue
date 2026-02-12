<template>
  <div class="bg-white shadow-lg rounded-lg border-2 theme-card p-6 max-w-2xl">
    <h2 class="text-lg font-semibold text-gray-800 mb-4">Configuração Fiscal (Certificado A1)</h2>
    <p class="text-sm text-gray-600 mb-4">Configure o certificado digital A1 (PFX) para consultar NF-e na SEFAZ via NFeDistribuicaoDFe.</p>
    <form @submit.prevent="save" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">CNPJ</label>
        <input
          v-model="form.cnpj"
          type="text"
          placeholder="Apenas números (14 dígitos)"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono"
          maxlength="18"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">UF</label>
        <input
          v-model="form.uf"
          type="text"
          placeholder="Ex: SP"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 uppercase"
          maxlength="2"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Arquivo PFX (.pfx)</label>
        <input
          type="file"
          ref="pfxInput"
          accept=".pfx,.p12"
          @change="onFileSelect"
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-orange-100 file:text-orange-800"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Senha do certificado</label>
        <input
          v-model="form.pfx_password"
          type="password"
          placeholder="Senha do PFX"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <p v-if="success" class="text-sm text-green-600">{{ success }}</p>
      <button
        type="submit"
        :disabled="saving"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ saving ? 'Salvando...' : 'Salvar configuração' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fiscalService } from '@/services/fiscal'

const form = ref({
  cnpj: '',
  uf: '',
  pfx_password: '',
})
const pfxInput = ref(null)
const pfxFile = ref(null)
const saving = ref(false)
const error = ref('')
const success = ref('')

function onFileSelect(e) {
  pfxFile.value = e.target?.files?.[0] || null
}

async function save() {
  const cnpj = (form.value.cnpj || '').replace(/\D/g, '')
  if (cnpj.length !== 14) {
    error.value = 'CNPJ deve ter 14 dígitos.'
    return
  }
  if ((form.value.uf || '').trim().length !== 2) {
    error.value = 'Informe a UF (2 caracteres).'
    return
  }
  if (!pfxFile.value) {
    error.value = 'Selecione o arquivo PFX.'
    return
  }
  if (!form.value.pfx_password) {
    error.value = 'Informe a senha do certificado.'
    return
  }
  error.value = ''
  success.value = ''
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('cnpj', cnpj)
    fd.append('uf', (form.value.uf || '').toUpperCase().trim())
    fd.append('pfx_file', pfxFile.value)
    fd.append('pfx_password', form.value.pfx_password)
    await fiscalService.saveConfig(fd)
    success.value = 'Configuração salva com sucesso.'
    if (pfxInput.value) pfxInput.value.value = ''
    pfxFile.value = null
    form.value.pfx_password = ''
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao salvar. Verifique o certificado e a senha.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const res = await fiscalService.getConfig()
    const data = res.data
    if (data) {
      form.value.cnpj = data.cnpj || ''
      form.value.uf = data.uf || ''
    }
  } catch {
    // sem config ainda
  }
})
</script>
