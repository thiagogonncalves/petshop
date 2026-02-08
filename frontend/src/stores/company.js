import { defineStore } from 'pinia'
import { companyService } from '@/services/company'
import { mediaUrl } from '@/utils/mediaUrl'

export const useCompanyStore = defineStore('company', {
  state: () => ({
    company: null,
  }),

  getters: {
    logoUrl: (state) => mediaUrl(state.company?.logo_url) || null,
    companyName: (state) => state.company?.name || 'GB PET',
    theme: (state) => state.company?.theme || 'orange',
  },

  actions: {
    async fetchCompany() {
      try {
        const { data } = await companyService.get()
        this.company = data || null
        document.title = (data?.name || 'GB PET')
        document.body.setAttribute('data-theme', this.theme)
      } catch {
        this.company = null
        document.body.setAttribute('data-theme', 'orange')
      }
    },
    setTheme(theme) {
      if (this.company) this.company.theme = theme
      document.body.setAttribute('data-theme', theme)
    },
  },
})
