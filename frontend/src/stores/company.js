import { defineStore } from 'pinia'
import { companyService } from '@/services/company'

export const useCompanyStore = defineStore('company', {
  state: () => ({
    company: null,
  }),

  getters: {
    logoUrl: (state) => state.company?.logo_url || null,
    companyName: (state) => state.company?.name || 'GB PET',
  },

  actions: {
    async fetchCompany() {
      try {
        const { data } = await companyService.get()
        this.company = data || null
      } catch {
        this.company = null
      }
    },
  },
})
