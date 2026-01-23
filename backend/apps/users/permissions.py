"""
Custom permissions for RBAC
"""
from rest_framework import permissions
from .models import UserRole


class IsAdmin(permissions.BasePermission):
    """Only admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsAdminOrManager(permissions.BasePermission):
    """Admin or Manager users"""
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and
            request.user.role in [UserRole.ADMIN, UserRole.MANAGER]
        )


class IsAdminOrManagerOrReadOnly(permissions.BasePermission):
    """Admin/Manager can write, others can only read"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user and request.user.is_authenticated and
            request.user.role in [UserRole.ADMIN, UserRole.MANAGER]
        )


class CanManageUsers(permissions.BasePermission):
    """Can manage users (Admin and Manager, but Manager can't modify Admin)"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.role == UserRole.ADMIN:
            return True
        
        if request.user.role == UserRole.MANAGER:
            # Manager can manage users, but check in has_object_permission for Admin protection
            return True
        
        return False

    def has_object_permission(self, request, view, obj):
        # Managers cannot modify admins
        if request.user.role == UserRole.MANAGER and obj.role == UserRole.ADMIN:
            return False
        return True


class CanViewReports(permissions.BasePermission):
    """Can view reports (all authenticated, but limited for regular users)"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
