"""
URLs para configurações (admin).
"""
from django.urls import path
from . import settings_views

urlpatterns = [
    path('business-hours/', settings_views.business_hours),
    path('closures/', settings_views.closures_list),
    path('closures/<int:pk>/', settings_views.closure_delete),
]
