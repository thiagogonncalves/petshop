"""
Client views
"""
from rest_framework import viewsets
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
