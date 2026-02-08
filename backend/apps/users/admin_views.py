"""
Admin-only views: user management and roles (admin area).
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole, Role, CompanySettings
from .models import PERMISSION_CHOICES
from .permissions import IsAdmin
from .admin_serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    RoleSerializer,
    RoleCreateUpdateSerializer,
    CompanySettingsSerializer,
)


class AdminUserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin-only user management.
    List, create, retrieve, update, toggle-active, set-password.
    """
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [IsAdmin]
    pagination_class = AdminUserPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return AdminUserListSerializer
        if self.action == 'create':
            return AdminUserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return AdminUserUpdateSerializer
        return AdminUserDetailSerializer

    def get_queryset(self):
        qs = User.objects.all().order_by('-created_at')
        q = (self.request.query_params.get('q') or '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(email__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            AdminUserDetailSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response(AdminUserDetailSerializer(user).data)

    @action(detail=True, methods=['post'], url_path='set-password')
    def set_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get('password')
        if not new_password:
            return Response(
                {'password': ['Campo obrigatório']},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response(
                {'password': list(e.messages) if hasattr(e, 'messages') else [str(e)]},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Senha alterada com sucesso.'})


class AdminRoleViewSet(viewsets.ModelViewSet):
    """
    CRUD de perfis (Role) customizados + lista de permissões.
    """
    queryset = Role.objects.all().order_by('name')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RoleCreateUpdateSerializer
        return RoleSerializer


class AdminPermissionsViewSet(viewsets.ViewSet):
    """
    Lista de códigos de permissão do sistema (para multi-select na UI).
    """
    permission_classes = [IsAdmin]

    def list(self, request):
        return Response([{'code': c[0], 'label': c[1]} for c in PERMISSION_CHOICES])


class AdminRoleOptionsViewSet(viewsets.ViewSet):
    """
    Opções de perfil para dropdown: built-in (admin, manager, user) + perfis customizados.
    """
    permission_classes = [IsAdmin]

    def list(self, request):
        builtin = [
            {'value': 'admin', 'label': 'Administrador', 'type': 'builtin'},
            {'value': 'manager', 'label': 'Gerente', 'type': 'builtin'},
            {'value': 'user', 'label': 'Usuário', 'type': 'builtin'},
        ]
        custom = [{'value': f'role_{r.id}', 'label': r.name, 'type': 'custom', 'id': r.id} for r in Role.objects.all()]
        return Response(builtin + custom)


class CompanySettingsViewSet(viewsets.ModelViewSet):
    """
    Dados da empresa (singleton): GET e PATCH. Usado em Administração > Dados da empresa.
    """
    permission_classes = [IsAdmin]
    serializer_class = CompanySettingsSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ['get', 'head', 'options', 'patch', 'post']
    pagination_class = None

    def get_queryset(self):
        obj, _ = CompanySettings.objects.get_or_create(
            defaults={'name': '', 'cpf_cnpj': '', 'address': '', 'address_number': '', 'theme': 'orange'}
        )
        return CompanySettings.objects.filter(pk=obj.pk)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def logo(self, request, pk=None):
        """Upload de logo + dados: POST multipart com logo (arquivo) e demais campos."""
        import os
        import re
        import uuid
        from django.conf import settings
        obj = self.get_object()
        file_obj = request.FILES.get('logo')
        if not file_obj:
            return Response({'detail': 'Campo logo obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        # Garantir caminho absoluto (crítico para Docker/volume)
        media_root = os.path.abspath(str(settings.MEDIA_ROOT))
        dir_path = os.path.join(media_root, 'company')
        os.makedirs(dir_path, exist_ok=True)
        # Nome seguro para URL (sem espaços, &, acentos - evita 404 ao carregar a imagem)
        base = re.sub(r'[^\w\-]', '_', os.path.splitext(file_obj.name)[0])[:50] or 'logo'
        ext = os.path.splitext(file_obj.name)[1].lower() or '.png'
        if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
            ext = '.png'
        filename = f'{base}_{uuid.uuid4().hex[:8]}{ext}'
        rel_path = f'company/{filename}'
        full_path = os.path.join(dir_path, filename)
        # Gravação direta em disco (evita problemas do FileSystemStorage no Docker)
        with open(full_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        if obj.logo:
            try:
                old_path = os.path.join(media_root, str(obj.logo))
                if os.path.isfile(old_path):
                    os.remove(old_path)
            except Exception:
                pass
        obj.logo = rel_path
        for field in ('name', 'cpf_cnpj', 'address', 'address_number'):
            if field in request.data:
                setattr(obj, field, request.data.get(field) or '')
        obj.save()
        serializer = CompanySettingsSerializer(obj)
        return Response(serializer.data)
