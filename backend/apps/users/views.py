"""
User views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, CompanySettings
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer, LoginSerializer
)
from .admin_serializers import CompanySettingsSerializer
from .permissions import CanManageUsers, IsAdminOrManager


class CompanySettingsPublicAPIView(APIView):
    """GET dados da empresa (público: login, PDV, cupom)."""
    permission_classes = [AllowAny]

    def get(self, request):
        obj = CompanySettings.objects.first()
        if not obj:
            obj = CompanySettings.objects.create(name='', cpf_cnpj='', address='', address_number='')
        serializer = CompanySettingsSerializer(obj, context={'request': request})
        data = dict(serializer.data)
        data['show_first_login_instructions'] = User.objects.filter(must_change_password=True).exists()
        return Response(data)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management
    """
    queryset = User.objects.all()
    permission_classes = [CanManageUsers]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        elif user.role == 'manager':
            # Manager can see all except admins (can modify but not see them)
            return User.objects.exclude(role='admin')
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrManager])
    def me(self, request):
        """Get current user info"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[])
    def login(self, request):
        """Custom login endpoint"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None or not user.is_active:
            return Response(
                {'error': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        user_data = UserSerializer(user).data
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
            'must_change_password': getattr(user, 'must_change_password', False),
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def first_login_change_password(request):
    """
    Primeiro login: altera usuário e senha padrão.
    POST /api/auth/first-login/
    Body: { new_username, new_password, new_password_confirm }
    """
    user = request.user
    if not getattr(user, 'must_change_password', False):
        return Response(
            {'detail': 'Você já alterou sua senha.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    new_username = request.data.get('new_username', '').strip()
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    if not new_username:
        return Response(
            {'new_username': ['Informe o novo usuário (e-mail).']},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not new_password:
        return Response(
            {'new_password': ['Informe a nova senha.']},
            status=status.HTTP_400_BAD_REQUEST
        )
    if new_password != new_password_confirm:
        return Response(
            {'new_password_confirm': ['As senhas não coincidem.']},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        validate_password(new_password, user)
    except Exception as e:
        return Response(
            {'new_password': list(e.messages) if hasattr(e, 'messages') else [str(e)]},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
        return Response(
            {'new_username': ['Este usuário já está em uso.']},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.username = new_username
    user.email = new_username
    user.set_password(new_password)
    user.must_change_password = False
    user.save(update_fields=['username', 'email', 'password', 'must_change_password', 'updated_at'])
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'must_change_password': False,
    })
