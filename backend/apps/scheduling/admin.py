from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'pet', 'service', 'scheduled_date', 'status', 'created_at')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('client__name', 'pet__name', 'service__name')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
