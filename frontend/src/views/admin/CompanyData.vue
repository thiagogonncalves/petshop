<template>
  <div>
    <div class="flex items-center mb-6">
      <svg class="w-7 h-7 text-orange-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
      </svg>
      <h1 class="text-2xl font-bold text-gray-800">Dados da empresa</h1>
    </div>

    <div class="bg-white rounded-lg shadow border-2 border-orange-200 p-6 max-w-2xl">
      <p class="text-sm text-gray-600 mb-4">Logo e dados exibidos na tela de login, no PDV e no cupom.</p>

      <form @submit.prevent="save">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Logo (PNG)</label>
          <div class="flex items-start gap-4">
            <div class="w-28 h-28 rounded-lg border-2 border-gray-200 bg-gray-50 flex items-center justify-center overflow-hidden flex-shrink-0">
              <img v-if="imagePreviewUrl" :src="imagePreviewUrl" alt="Logo" class="w-full h-full object-contain" />
              <svg v-else class="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <input
                ref="fileInputRef"
                type="file"
                accept="image/png,image/*"
                class="block w-full text-sm text-gray-500 file:mr-2 file:py-2 file:px-4 file:rounded file:border-0 file:bg-orange-100 file:text-orange-700 hover:file:bg-orange-200"
                @change="onImageSelect"
              />
            </div>
          </div>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Nome da empresa</label>
          <input v-model="form.name" type="text" placeholder="Ex: GB PET"
                 class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">CPF/CNPJ</label>
          <input v-model="form.cpf_cnpj" type="text" placeholder="00.000.000/0001-00"
                 class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Endereço</label>
            <input v-model="form.address" type="text" placeholder="Rua, bairro, cidade"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Número</label>
            <input v-model="form.address_number" type="text" placeholder="Nº"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
          </div>
        </div>

        <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>

        <div class="flex gap-3">
          <button type="submit" :disabled="saving"
                  class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50">
            {{ saving ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminCompanyService } from '@/services/company'
import { useCompanyStore } from '@/stores/company'

const form = ref({
  name: '',
  cpf_cnpj: '',
  address: '',
  address_number: '',
})
const companyId = ref(null)
const loadedLogoUrl = ref(null)
const imageFile = ref(null)
const imagePreviewUrl = ref(null)
const fileInputRef = ref(null)
const saving = ref(false)
const error = ref('')
const companyStore = useCompanyStore()

function onImageSelect(e) {
  const file = e.target.files?.[0]
  imageFile.value = file || null
  if (imagePreviewUrl.value && imagePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  imagePreviewUrl.value = null
  if (file) {
    imagePreviewUrl.value = URL.createObjectURL(file)
  } else if (loadedLogoUrl.value) {
    imagePreviewUrl.value = loadedLogoUrl.value
  }
}

async function load() {
  try {
    const { data } = await adminCompanyService.get()
    if (data && data.id) {
      companyId.value = data.id
      form.value = {
        name: data.name ?? '',
        cpf_cnpj: data.cpf_cnpj ?? '',
        address: data.address ?? '',
        address_number: data.address_number ?? '',
      }
      if (data.logo_url) {
        loadedLogoUrl.value = data.logo_url
        imagePreviewUrl.value = data.logo_url
      } else {
        loadedLogoUrl.value = null
      }
    }
  } catch (err) {
    console.error(err)
    error.value = 'Erro ao carregar dados da empresa.'
  }
}

async function save() {
  if (!companyId.value) return
  error.value = ''
  saving.value = true
  try {
    if (imageFile.value) {
      const fd = new FormData()
      fd.append('name', form.value.name)
      fd.append('cpf_cnpj', form.value.cpf_cnpj)
      fd.append('address', form.value.address)
      fd.append('address_number', form.value.address_number)
      fd.append('logo', imageFile.value)
      await adminCompanyService.update(companyId.value, fd)
    } else {
      await adminCompanyService.update(companyId.value, {
        name: form.value.name,
        cpf_cnpj: form.value.cpf_cnpj,
        address: form.value.address,
        address_number: form.value.address_number,
      })
    }
    imageFile.value = null
    await load()
    await companyStore.fetchCompany()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  load()
})
</script>
