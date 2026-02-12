"""
Contas a pagar - views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import BillPayable
from .serializers import BillPayableSerializer


class BillPayableViewSet(viewsets.ModelViewSet):
    queryset = BillPayable.objects.all()
    serializer_class = BillPayableSerializer
    filterset_fields = ['status']
    search_fields = ['description', 'provider']

    def get_queryset(self):
        queryset = BillPayable.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('due_date', '-created_at')

    @action(detail=False, methods=['get'], url_path='alerts')
    def alerts(self, request):
        """
        Retorna contas que vencem hoje e contas em atraso, para exibir no sino.
        """
        today = timezone.localdate()
        base_qs = BillPayable.objects.filter(status__in=['pending', 'overdue'])

        overdue_qs = base_qs.filter(due_date__lt=today).order_by('due_date')
        due_today_qs = base_qs.filter(due_date=today).order_by('due_date')

        overdue_count = overdue_qs.count()
        due_today_count = due_today_qs.count()

        items = list(due_today_qs[:15]) + list(overdue_qs[:15])
        serializer = BillPayableSerializer(items, many=True)

        return Response({
            'overdue_count': overdue_count,
            'due_today_count': due_today_count,
            'items': serializer.data,
        })

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Marcar conta como paga."""
        bill = self.get_object()
        if bill.status in ('paid', 'cancelled'):
            return Response(
                {'detail': 'Esta conta já está paga ou cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        paid_date = request.data.get('paid_date') or timezone.localdate()
        bill.paid_date = paid_date
        bill.status = 'paid'
        bill.save()
        serializer = self.get_serializer(bill)
        return Response(serializer.data)
