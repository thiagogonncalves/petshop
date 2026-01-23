"""
Reports views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from apps.sales.models import Sale
from apps.products.models import Product, StockMovement
from apps.clients.models import Client
from apps.pets.models import Pet
from apps.scheduling.models import Appointment


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for Reports
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def sales_summary(self, request):
        """Sales summary by period"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            start_date = (timezone.now() - timedelta(days=30)).date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = timezone.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        sales = Sale.objects.filter(
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date
        )
        
        total_sales = sales.aggregate(
            total=Sum('total'),
            count=Count('id')
        )
        
        by_status = sales.values('status').annotate(
            total=Sum('total'),
            count=Count('id')
        )
        
        by_payment_method = sales.values('payment_method').annotate(
            total=Sum('total'),
            count=Count('id')
        )
        
        daily_sales = sales.annotate(date=TruncDate('sale_date')).values('date').annotate(
            total=Sum('total'),
            count=Count('id')
        ).order_by('date')
        
        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': total_sales,
            'by_status': list(by_status),
            'by_payment_method': list(by_payment_method),
            'daily_sales': list(daily_sales)
        })

    @action(detail=False, methods=['get'])
    def inventory_status(self, request):
        """Inventory status report"""
        products = Product.objects.filter(is_active=True)
        
        low_stock = products.filter(
            stock_quantity__lte=F('min_stock')
        ).values('id', 'name', 'stock_quantity', 'min_stock')
        
        out_of_stock = products.filter(stock_quantity=0).values('id', 'name')
        
        total_value = sum(p.stock_quantity * p.cost_price for p in products)
        
        return Response({
            'total_products': products.count(),
            'low_stock_count': low_stock.count(),
            'out_of_stock_count': out_of_stock.count(),
            'total_inventory_value': float(total_value),
            'low_stock_items': list(low_stock),
            'out_of_stock_items': list(out_of_stock)
        })

    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """Top selling products"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = (timezone.now() - timedelta(days=30)).date()
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        from apps.sales.models import SaleItem
        
        top_products = SaleItem.objects.filter(
            item_type='product',
            sale__sale_date__date__gte=start_date,
            sale__sale_date__date__lte=end_date,
            sale__status='paid'
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total')
        ).order_by('-total_revenue')[:10]
        
        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'top_products': list(top_products)
        })

    @action(detail=False, methods=['get'])
    def clients_summary(self, request):
        """Clients summary"""
        total_clients = Client.objects.filter(is_active=True).count()
        clients_with_sales = Client.objects.filter(
            is_active=True,
            sales__isnull=False
        ).distinct().count()
        
        top_clients = Client.objects.filter(
            is_active=True
        ).annotate(
            total_sales=Sum('sales__total'),
            sales_count=Count('sales')
        ).order_by('-total_sales')[:10]
        
        return Response({
            'total_clients': total_clients,
            'clients_with_sales': clients_with_sales,
            'top_clients': [
                {
                    'id': c.id,
                    'name': c.name,
                    'total_sales': float(c.total_sales or 0),
                    'sales_count': c.sales_count
                }
                for c in top_clients
            ]
        })

    @action(detail=False, methods=['get'])
    def appointments_summary(self, request):
        """Appointments summary"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = (timezone.now() - timedelta(days=30)).date()
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        appointments = Appointment.objects.filter(
            scheduled_date__date__gte=start_date,
            scheduled_date__date__lte=end_date
        )
        
        by_status = appointments.values('status').annotate(count=Count('id'))
        
        by_service = appointments.values('service__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total': appointments.count(),
            'by_status': list(by_status),
            'by_service': list(by_service)
        })

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard summary"""
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        
        # Sales
        today_sales = Sale.objects.filter(sale_date__date=today).aggregate(
            total=Sum('total'),
            count=Count('id')
        )
        
        month_sales = Sale.objects.filter(
            sale_date__date__gte=this_month_start
        ).aggregate(
            total=Sum('total'),
            count=Count('id')
        )
        
        # Appointments
        today_appointments = Appointment.objects.filter(
            scheduled_date__date=today,
            status__in=['scheduled', 'in_progress']
        ).count()
        
        upcoming_appointments = Appointment.objects.filter(
            scheduled_date__gte=timezone.now(),
            status__in=['scheduled', 'in_progress']
        ).count()
        
        # Inventory
        low_stock_count = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=F('min_stock')
        ).count()
        
        # Clients
        total_clients = Client.objects.filter(is_active=True).count()
        total_pets = Pet.objects.filter(is_active=True).count()
        
        return Response({
            'sales': {
                'today': today_sales,
                'this_month': month_sales
            },
            'appointments': {
                'today': today_appointments,
                'upcoming': upcoming_appointments
            },
            'inventory': {
                'low_stock_count': low_stock_count
            },
            'clients': {
                'total': total_clients,
                'total_pets': total_pets
            }
        })
