"""
Scheduling views
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Appointment management
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filterset_fields = ['client', 'pet', 'service', 'status']
    search_fields = ['client__name', 'pet__name', 'service__name']

    def get_queryset(self):
        queryset = Appointment.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_at__lte=end_date)
        
        return queryset

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments"""
        appointments = Appointment.objects.filter(
            start_at__gte=timezone.now(),
            status__in=['scheduled', 'confirmed', 'in_progress']
        ).order_by('start_at')[:20]
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        today = timezone.now().date()
        appointments = Appointment.objects.filter(
            start_at__date=today,
            status__in=['scheduled', 'confirmed', 'in_progress']
        ).order_by('start_at')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel appointment"""
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
