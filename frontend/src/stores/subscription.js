import { defineStore } from 'pinia'
import { subscriptionService } from '@/services/subscription'

export const useSubscriptionStore = defineStore('subscription', {
  state: () => ({
    status: 'trial',
    canWrite: true,
    daysRemainingTrial: 7,
    trialEnd: null,
    plan: null,
    currentPeriodEnd: null,
  }),

  getters: {
    isTrial: (state) => state.status === 'trial',
    isActive: (state) => state.status === 'active',
    isReadOnly: (state) => !state.canWrite,
  },

  actions: {
    async fetchStatus() {
      try {
        const { data } = await subscriptionService.getStatus()
        this.status = data.status || 'trial'
        this.canWrite = data.can_write !== false
        this.daysRemainingTrial = data.days_remaining_trial ?? 0
        this.trialEnd = data.trial_end
        this.plan = data.plan
        this.currentPeriodEnd = data.current_period_end
        return data
      } catch (err) {
        // Em caso de erro (ex: 403), marcar como read-only
        if (err.response?.status === 403 && err.response?.data?.detail === 'subscription_expired') {
          this.canWrite = false
          this.status = 'expired'
        }
        throw err
      }
    },

    async createPayment() {
      const { data } = await subscriptionService.pay()
      return data
    },

    reset() {
      this.status = 'trial'
      this.canWrite = true
      this.daysRemainingTrial = 7
      this.trialEnd = null
      this.plan = null
      this.currentPeriodEnd = null
    },
  },
})
