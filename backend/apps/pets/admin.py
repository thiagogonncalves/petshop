from django.contrib import admin
from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'client', 'is_active', 'created_at')
    list_filter = ('species', 'sex', 'is_active', 'created_at')
    search_fields = ('name', 'breed', 'client__name')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
