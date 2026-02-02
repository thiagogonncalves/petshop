"""
Client views
"""
import re
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client management
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filterset_fields = ['is_active', 'document_type']
    search_fields = ['name', 'document', 'email', 'phone']

    def get_queryset(self):
        queryset = Client.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @action(detail=True, methods=['get'])
    def pets(self, request, pk=None):
        """Get all pets of a client"""
        client = self.get_object()
        from apps.pets.serializers import PetSerializer
        pets = client.pets.all()
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-cpf')
    def by_cpf(self, request):
        """PDV: get client by CPF (document, digits only). Returns 404 if not found."""
        cpf_raw = request.query_params.get('cpf') or ''
        cpf = re.sub(r'[^0-9]', '', cpf_raw)
        if len(cpf) != 11:
            return Response(
                {'detail': 'CPF inválido. Informe 11 dígitos.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        client = Client.objects.filter(is_active=True, document_type='cpf', document=cpf).first()
        if not client:
            return Response({'detail': 'Cliente não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(client)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def credits(self, request, pk=None):
        """Histórico de crediários do cliente."""
        client = self.get_object()
        from apps.sales.models import CreditAccount
        from apps.sales.serializers import CreditAccountListSerializer
        accounts = CreditAccount.objects.filter(client=client).select_related('sale').prefetch_related('installments').order_by('-created_at')
        serializer = CreditAccountListSerializer(accounts, many=True)
        return Response(serializer.data)
