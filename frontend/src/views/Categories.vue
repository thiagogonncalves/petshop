<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <svg class="w-7 h-7 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 24 24">
          <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z"/>
        </svg>
        <h1 class="text-2xl font-bold text-blue-800">Categorias</h1>
      </div>
      <button
        type="button"
        :disabled="!subscriptionStore.canWrite"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="openModal()"
      >
        Nova Categoria
      </button>
    </div>

    <div class="bg-white shadow-lg rounded-lg overflow-hidden border-2 border-orange-200">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-orange-400 to-orange-300">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Descrição</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="cat in categories" :key="cat.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ cat.name }}</td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{{ cat.description || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="cat.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ cat.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button type="button" :disabled="!subscriptionStore.canWrite" class="text-blue-600 hover:text-blue-800 mr-4 disabled:opacity-50 disabled:cursor-not-allowed" @click="openModal(cat)">Editar</button>
              <button type="button" :disabled="!subscriptionStore.canWrite" class="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed" @click="deleteCategory(cat.id)">Excluir</button>
            </td>
          </tr>
          <tr v-if="categories.length === 0">
            <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">Nenhuma categoria cadastrada</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Nova/Editar Categoria -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="closeModal">
      <div class="relative top-10 mx-auto p-6 border-2 border-orange-300 w-full max-w-md shadow-2xl rounded-xl bg-white">
        <h3 class="text-xl font-bold text-blue-800 mb-4">{{ editingCategory ? 'Editar Categoria' : 'Nova Categoria' }}</h3>
        <form @submit.prevent="saveCategory">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="form.name" type="text" required placeholder="Ex: Rações"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
            <textarea v-model="form.description" rows="2" placeholder="Descrição da categoria"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"></textarea>
          </div>
          <div v-if="editingCategory" class="mb-4">
            <label class="flex items-center gap-2">
              <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
              <span class="text-sm text-gray-700">Ativo</span>
            </label>
          </div>
          <p v-if="formError" class="mb-2 text-sm text-red-600">{{ formError }}</p>
          <div class="flex justify-end gap-3">
            <button type="button" @click="closeModal"
                    class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              {{ editingCategory ? 'Salvar' : 'Criar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { productsService } from '@/services/products'
import { useSubscriptionStore } from '@/stores/subscription'

const subscriptionStore = useSubscriptionStore()
const categories = ref([])
const showModal = ref(false)
const editingCategory = ref(null)
const formError = ref('')
const form = ref({
  name: '',
  description: '',
  is_active: true,
})

const loadCategories = async () => {
  try {
    const response = await productsService.getCategories()
    categories.value = response.data.results ?? response.data
  } catch (error) {
    console.error('Erro ao carregar categorias:', error)
    alert('Erro ao carregar categorias')
  }
}

const openModal = (cat = null) => {
  editingCategory.value = cat ?? null
  form.value = {
    name: cat?.name ?? '',
    description: cat?.description ?? '',
    is_active: cat !== null ? cat.is_active : true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
}

const saveCategory = async () => {
  formError.value = ''
  try {
    const payload = {
      name: form.value.name.trim(),
      description: (form.value.description || '').trim(),
    }
    if (editingCategory.value) {
      payload.is_active = form.value.is_active
      await productsService.updateCategory(editingCategory.value.id, payload)
      alert('Categoria atualizada com sucesso!')
    } else {
      await productsService.createCategory(payload)
      alert('Categoria criada com sucesso!')
    }
    await loadCategories()
    closeModal()
  } catch (err) {
    formError.value = err.response?.data?.name?.[0] ?? err.response?.data?.detail ?? err.response?.data?.error ?? 'Erro ao salvar categoria'
  }
}

const deleteCategory = async (id) => {
  if (!confirm('Excluir esta categoria? Produtos vinculados podem ser afetados.')) return
  try {
    await productsService.deleteCategory(id)
    await loadCategories()
    alert('Categoria excluída.')
  } catch (err) {
    const msg = err.response?.data?.detail ?? err.response?.data?.error ?? 'Erro ao excluir categoria'
    alert(msg)
  }
}

onMounted(() => {
  loadCategories()
})
</script>
