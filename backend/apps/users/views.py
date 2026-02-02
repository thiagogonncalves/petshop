"""
User views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
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
        return Response(serializer.data)


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
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
