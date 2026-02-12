"""
URLs do módulo fiscal.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'nfe', views.NFeImportViewSet, basename='fiscal-nfe')

urlpatterns = [
    path('config/', views.FiscalConfigView.as_view(), name='fiscal-config'),
    path('nfe/import-by-key/', views.NFeImportByKeyView.as_view(), name='fiscal-nfe-import-by-key'),
    path('nfe/sync/', views.NFeSyncView.as_view(), name='fiscal-nfe-sync'),
    path('nfe/<int:pk>/xml/', views.NFeXmlDownloadView.as_view(), name='fiscal-nfe-xml'),
    path('', include(router.urls)),
]
