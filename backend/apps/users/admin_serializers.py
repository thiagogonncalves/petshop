"""
Serializers for admin-only user management.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole, Role, RolePermission, CompanySettings


class AdminUserListSerializer(serializers.ModelSerializer):
    """List view: basic fields, no password."""
    role_display = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'custom_role', 'is_active', 'created_at'
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_role_display(self, obj):
        if obj.custom_role_id:
            return obj.custom_role.name
        return obj.get_role_display()


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Detail view: all safe fields."""
    role_display = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    custom_role_name = serializers.SerializerMethodField()

    def get_custom_role_name(self, obj):
        return obj.custom_role.name if obj.custom_role_id else None

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'custom_role', 'custom_role_name', 'phone', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_role_display(self, obj):
        if obj.custom_role_id:
            return obj.custom_role.name
        return obj.get_role_display()


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Create user (admin only)."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'custom_role', 'phone', 'is_active'
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'As senhas não coincidem.'})
        if attrs.get('custom_role') and attrs.get('role') != UserRole.USER:
            attrs['role'] = UserRole.USER
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Update user (admin only). Password optional."""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'custom_role', 'phone', 'is_active'
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class RoleOptionSerializer(serializers.Serializer):
    """For role options in dropdowns."""
    value = serializers.CharField()
    label = serializers.CharField()


# --- Perfis (Role) CRUD ---

class RoleSerializer(serializers.ModelSerializer):
    """List/detail Role with permissions."""
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_permissions(self, obj):
        return list(obj.permissions.values_list('permission_code', flat=True))


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/update Role with permissions list."""
    permissions = serializers.ListField(child=serializers.CharField(), write_only=True, required=False, default=list)

    class Meta:
        model = Role
        fields = ['name', 'code', 'description', 'permissions']

    def create(self, validated_data):
        perms = validated_data.pop('permissions', [])
        role = Role.objects.create(**validated_data)
        for code in perms:
            RolePermission.objects.get_or_create(role=role, permission_code=code)
        return role

    def update(self, instance, validated_data):
        perms = validated_data.pop('permissions', None)
        instance.name = validated_data.get('name', instance.name)
        instance.code = validated_data.get('code', instance.code)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        if perms is not None:
            instance.permissions.all().delete()
            for code in perms:
                RolePermission.objects.get_or_create(role=instance, permission_code=code)
        return instance


class CompanySettingsSerializer(serializers.ModelSerializer):
    """Dados da empresa (leitura: inclui logo_url para frontend)."""
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanySettings
        fields = ['id', 'name', 'cpf_cnpj', 'address', 'address_number', 'logo', 'logo_url', 'theme']
        read_only_fields = ['id', 'logo_url']

    def update(self, instance, validated_data):
        import os
        from django.conf import settings
        # Limpar referência órfã (arquivo não existe) antes de salvar novo - evita erro ao substituir
        if instance.logo and 'logo' in validated_data:
            path = os.path.join(settings.MEDIA_ROOT, str(instance.logo))
            if not os.path.isfile(path):
                instance.logo = None  # evita que Django tente deletar arquivo inexistente
        # Garantir que o diretório media/company existe antes do save (importante em Docker/volume novo)
        if 'logo' in validated_data:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'company'), exist_ok=True)
        return super().update(instance, validated_data)

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        # Se o arquivo não existir em disco (referência órfã), não retornar URL
        from django.conf import settings
        import os
        path = os.path.join(settings.MEDIA_ROOT, str(obj.logo))
        if not os.path.isfile(path):
            return None
        url = obj.logo.url
        return url if url.startswith('/') else f'/{url}'
