from django.contrib import admin
from .models import BillPayable


@admin.register(BillPayable)
class BillPayableAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'due_date', 'status', 'provider']
    list_filter = ['status']
    search_fields = ['description', 'provider']
    date_hierarchy = 'due_date'
