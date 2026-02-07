"""
User URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, CompanySettingsPublicAPIView, first_login_change_password

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('company/', CompanySettingsPublicAPIView.as_view(), name='company-settings-public'),
    path('first-login/', first_login_change_password, name='first-login'),
]
