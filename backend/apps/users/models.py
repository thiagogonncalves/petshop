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


# Lista de códigos de permissão do sistema (para UI e validação)
PERMISSION_CHOICES = [
    ('view_users', 'Ver usuários'),
    ('add_users', 'Criar usuários'),
    ('change_users', 'Editar usuários'),
    ('delete_users', 'Excluir usuários'),
    ('view_all_reports', 'Ver todos os relatórios'),
    ('view_limited_reports', 'Ver relatórios limitados'),
    ('manage_settings', 'Gerenciar configurações'),
    ('manage_integrations', 'Gerenciar integrações'),
    ('view_sales', 'Ver vendas'),
    ('add_sales', 'Registrar vendas'),
    ('view_inventory', 'Ver estoque'),
    ('view_clients', 'Ver clientes'),
    ('add_clients', 'Cadastrar clientes'),
    ('view_pets', 'Ver animais'),
    ('add_pets', 'Cadastrar animais'),
    ('view_services', 'Ver serviços'),
    ('add_services', 'Cadastrar serviços'),
    ('view_scheduling', 'Ver agendamentos'),
    ('add_scheduling', 'Criar agendamentos'),
]


class Role(models.Model):
    """
    Perfil (role) customizado: nome, código e permissões selecionáveis.
    Os perfis built-in (admin, manager, user) continuam no User.role (CharField).
    """
    name = models.CharField(max_length=100, verbose_name='Nome')
    code = models.SlugField(max_length=50, unique=True, verbose_name='Código')
    description = models.TextField(blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['name']

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Permissão atribuída a um perfil (Role)."""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission_code = models.CharField(max_length=50)

    class Meta:
        unique_together = [('role', 'permission_code')]
        verbose_name = 'Permissão do perfil'
        verbose_name_plural = 'Permissões do perfil'


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Perfil (built-in)'
    )
    custom_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Perfil customizado'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Formato de telefone inválido")],
        verbose_name='Telefone'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    must_change_password = models.BooleanField(
        default=False,
        verbose_name='Alterar senha no próximo login'
    )
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
        """Acesso ao menu Administração: perfil built-in admin ou superuser/staff."""
        return self.role == UserRole.ADMIN or getattr(self, 'is_superuser', False) or getattr(self, 'is_staff', False)

    @property
    def is_manager(self):
        """Gerente: perfil built-in manager ou admin."""
        if self.custom_role_id:
            return False
        return self.role in (UserRole.MANAGER, UserRole.ADMIN)

    def has_permission(self, permission_code):
        """
        Check if user has a specific permission.
        If custom_role is set, use RolePermission; else use built-in role permissions.
        """
        if self.is_superuser or self.is_staff:
            return True
        if self.custom_role_id:
            return self.custom_role.permissions.filter(permission_code=permission_code).exists()
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
                'view_pets', 'add_pets', 'view_limited_reports',
            ],
        }
        user_permissions = permissions.get(self.role, [])
        return permission_code in user_permissions


class ThemeChoice(models.TextChoices):
    ORANGE = 'orange', 'Laranja e Azul (padrão)'
    GREEN = 'green', 'Verde e Verde-água'
    PURPLE = 'purple', 'Roxo e Rosa'


class CompanySettings(models.Model):
    """
    Dados da empresa (singleton): logo, nome, CPF/CNPJ, endereço, tema.
    Usado na tela de login, PDV e cupom.
    """
    name = models.CharField(max_length=200, blank=True, verbose_name='Nome da empresa')
    cpf_cnpj = models.CharField(max_length=20, blank=True, verbose_name='CPF/CNPJ')
    address = models.CharField(max_length=300, blank=True, verbose_name='Endereço')
    address_number = models.CharField(max_length=20, blank=True, verbose_name='Número')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name='Logo (PNG)')
    theme = models.CharField(
        max_length=20,
        choices=ThemeChoice.choices,
        default=ThemeChoice.ORANGE,
        verbose_name='Tema de cores'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dados da empresa'
        verbose_name_plural = 'Dados da empresa'

    def __str__(self):
        return self.name or 'Dados da empresa'
