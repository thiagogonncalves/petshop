"""
User models with RBAC support
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Administrador'
    MANAGER = 'manager', 'Gerente'
    USER = 'user', 'Usuário'


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Perfil'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Formato de telefone inválido")],
        verbose_name='Telefone'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self):
        return self.role == UserRole.MANAGER

    def has_permission(self, permission_code):
        """
        Check if user has a specific permission based on role
        """
        permissions = {
            UserRole.ADMIN: [
                'view_users', 'add_users', 'change_users', 'delete_users',
                'view_all_reports', 'manage_settings', 'manage_integrations',
            ],
            UserRole.MANAGER: [
                'view_users', 'add_users', 'change_users',
                'view_all_reports', 'view_sales', 'view_inventory',
            ],
            UserRole.USER: [
                'add_sales', 'view_sales', 'add_clients', 'view_clients',
                'add_pets', 'view_pets', 'view_limited_reports',
            ],
        }
        user_permissions = permissions.get(self.role, [])
        return permission_code in user_permissions
