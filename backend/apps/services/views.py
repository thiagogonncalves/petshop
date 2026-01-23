"""
Service views
"""
from rest_framework import viewsets
from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Service management
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
