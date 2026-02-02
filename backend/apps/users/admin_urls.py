"""
Admin-only URL routes (user management, roles).
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import (
    AdminUserViewSet,
    AdminRoleViewSet,
    AdminPermissionsViewSet,
    AdminRoleOptionsViewSet,
    CompanySettingsViewSet,
)

router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'roles', AdminRoleViewSet, basename='admin-role')
router.register(r'permissions', AdminPermissionsViewSet, basename='admin-permissions')
router.register(r'role-options', AdminRoleOptionsViewSet, basename='admin-role-options')
router.register(r'company-settings', CompanySettingsViewSet, basename='admin-company-settings')

urlpatterns = [
    path('', include(router.urls)),
]
