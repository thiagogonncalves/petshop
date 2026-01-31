"""
NFe URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.NFeImportViewSet, basename='nfe-import')

urlpatterns = [
    path('import-xml/', views.NFeImportXMLView.as_view(), name='nfe-import-xml'),
    path('import-by-key/', views.NFeImportByKeyView.as_view(), name='nfe-import-by-key'),
    path('<int:import_id>/confirm/', views.NFeConfirmView.as_view(), name='nfe-confirm'),
    path('', include(router.urls)),
]
