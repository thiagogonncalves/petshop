from django.contrib import admin
from .models import Appointment, BusinessHoursConfig, BusinessHoursRule, BusinessClosure


class BusinessHoursRuleInline(admin.TabularInline):
    model = BusinessHoursRule
    extra = 0


@admin.register(BusinessHoursConfig)
class BusinessHoursConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'slot_minutes', 'timezone', 'updated_at')
    inlines = [BusinessHoursRuleInline]


@admin.register(BusinessClosure)
class BusinessClosureAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'pet', 'service', 'start_at', 'status', 'created_via', 'created_at')
    list_filter = ('status', 'created_via', 'created_at')
    search_fields = ('client__name', 'pet__name', 'service__name')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
