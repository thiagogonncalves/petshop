from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    list_filter = ('is_active',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'status', 'trial_start', 'trial_end', 'current_period_end')
    list_filter = ('status',)
    readonly_fields = ('company', 'mp_preference_id', 'mp_payment_id', 'created_at', 'updated_at')
