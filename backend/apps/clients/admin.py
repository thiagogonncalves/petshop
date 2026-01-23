from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'document_type', 'created_at')
    search_fields = ('name', 'document', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
