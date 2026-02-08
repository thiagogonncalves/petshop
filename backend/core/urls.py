"""
URL configuration for petshop project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Routes
    path('api/auth/', include('apps.users.urls')),
    path('api/admin/', include('apps.users.admin_urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/pets/', include('apps.pets.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/scheduling/', include('apps.scheduling.urls')),
    path('api/public/booking/', include('apps.scheduling.public_urls')),
    path('api/settings/', include('apps.scheduling.settings_urls')),
    path('api/sales/', include('apps.sales.urls')),
    path('api/credits/', include('apps.sales.credit_urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
    path('api/nfe/', include('apps.integrations.nfe.urls')),
    path('api/subscription/', include('apps.subscription.urls')),
]

# Media (uploads): sempre servir - nginx em produção faz proxy de /media/ para o backend
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
