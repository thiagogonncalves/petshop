"""
Reports views — read-only endpoints. All date filters use start/end (YYYY-MM-DD).
Default status: paid; use status= to include cancelled or other.
"""
import csv
from io import StringIO
from datetime import date, timedelta
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from apps.reports.services.queries import (
    dashboard_data,
    get_dashboard_summary,
    sales_report_queryset,
    products_sold,
    sales_ranking,
    low_stock,
    abc_products,
    services_sold,
    top_clients,
    sales_heatmap,
    profit_by_product,
    get_sellers,
)
from apps.reports.serializers import ReportSaleListSerializer


def _parse_params(request):
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    if end:
        try:
            end = date.fromisoformat(end)
        except ValueError:
            end = timezone.now().date()
    else:
        end = timezone.now().date()
    if start:
        try:
            start = date.fromisoformat(start)
        except ValueError:
            start = end - timedelta(days=30)
    else:
        start = end - timedelta(days=30)
    return start, end


class ReportPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ---------- Dashboard ----------
class DashboardSummaryView(APIView):
    """
    Dashboard resumido: KPIs, agenda do dia, alertas, clientes, gráficos, insights.
    GET /api/reports/dashboard-summary/?date=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)
        try:
            date_str = request.query_params.get('date')
            data = get_dashboard_summary(target_date=date_str)
            data = _serialize_decimals(data)
            return Response(data)
        except Exception as e:
            logger.exception('Erro ao carregar dashboard-summary')
            from django.conf import settings
            detail = str(e) if settings.DEBUG else 'Erro interno ao carregar relatório. Verifique se as migrações foram aplicadas (python manage.py migrate).'
            return Response({'detail': detail}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellersReportView(APIView):
    """List of users that have created sales (for filter dropdowns)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_sellers()
        return Response(data)


class DashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        user_id = request.query_params.get('user_id') or None
        payment_method = request.query_params.get('payment_method') or None
        status_filter = request.query_params.get('status') or 'paid'
        data = dashboard_data(
            start=start, end=end,
            user_id=user_id,
            payment_method=payment_method,
            status=status_filter,
        )
        # Serialize decimals for JSON
        def _serialize(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            if hasattr(obj, '__float__'):
                return float(obj)
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [_serialize(x) for x in obj]
            return obj
        data = _serialize(data)
        return Response(data)


# ---------- Sales list (paginated) ----------
class SalesReportView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ReportPagination

    def get(self, request):
        start, end = _parse_params(request)
        user_id = request.query_params.get('user_id') or None
        client_id = request.query_params.get('client_id') or None
        status_filter = request.query_params.get('status')
        search = request.query_params.get('q') or None
        exclude_cancelled = request.query_params.get('include_cancelled', 'false').lower() != 'true'
        qs = sales_report_queryset(
            start=start, end=end,
            user_id=user_id, client_id=client_id,
            status=status_filter,
            search=search,
            exclude_cancelled=exclude_cancelled,
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        serializer = ReportSaleListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ---------- Products sold ----------
class ProductsSoldReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        category_id = request.query_params.get('category_id') or None
        order = request.query_params.get('order') or 'revenue'
        limit = min(int(request.query_params.get('limit') or 100), 500)
        data = products_sold(start=start, end=end, category_id=category_id, order=order, limit=limit)
        data = _serialize_decimals(data)
        return Response({'results': data, 'period': {'start': start.isoformat(), 'end': end.isoformat()}})


# ---------- Sales ranking ----------
class SalesRankingReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        order = request.query_params.get('order') or 'revenue'
        limit = min(int(request.query_params.get('limit') or 20), 100)
        data = sales_ranking(start=start, end=end, order=order, limit=limit)
        data = _serialize_decimals(data)
        return Response({'results': data, 'period': {'start': start.isoformat(), 'end': end.isoformat()}})


# ---------- Low stock ----------
class LowStockReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        threshold = request.query_params.get('threshold')
        if threshold is not None:
            try:
                threshold = int(threshold)
            except ValueError:
                threshold = None
        data = low_stock(threshold=threshold)
        data = [dict(r) for r in data]
        for r in data:
            r['category_name'] = r.pop('category__name', None)
        return Response({'results': data})


# ---------- ABC products ----------
class ABCProductsReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        metric = request.query_params.get('metric') or 'revenue'
        data = abc_products(start=start, end=end, metric=metric)
        data = _serialize_decimals(data)
        return Response({'results': data, 'period': {'start': start.isoformat(), 'end': end.isoformat()}})


# ---------- Services sold ----------
class ServicesSoldReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        data = services_sold(start=start, end=end)
        data = _serialize_decimals(data)
        return Response({'results': data, 'period': {'start': start.isoformat(), 'end': end.isoformat()}})


# ---------- Top clients ----------
class TopClientsReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        order = request.query_params.get('order') or 'revenue'
        limit = min(int(request.query_params.get('limit') or 20), 100)
        data = top_clients(start=start, end=end, order=order, limit=limit)
        data = _serialize_decimals(data)
        return Response({'results': data, 'period': {'start': start.isoformat(), 'end': end.isoformat()}})


# ---------- Sales heatmap ----------
class SalesHeatmapReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        data = sales_heatmap(start=start, end=end)
        data['data'] = _serialize_decimals(data['data'])
        return Response(data)


# ---------- Profit by product ----------
class ProfitByProductReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        data = profit_by_product(start=start, end=end)
        data = _serialize_decimals(data)
        return Response({'results': data, 'period': {'start': start.isoformat(), 'end': end.isoformat()}})


def _serialize_decimals(obj):
    from decimal import Decimal
    if isinstance(obj, Decimal):
        return float(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize_decimals(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize_decimals(x) for x in obj]
    return obj


# ---------- CSV Exports ----------
class SalesExportCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        user_id = request.query_params.get('user_id') or None
        client_id = request.query_params.get('client_id') or None
        status_filter = request.query_params.get('status')
        exclude_cancelled = request.query_params.get('include_cancelled', 'false').lower() != 'true'
        qs = sales_report_queryset(
            start=start, end=end,
            user_id=user_id, client_id=client_id,
            status=status_filter,
            exclude_cancelled=exclude_cancelled,
        )[:5000]
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            'ID', 'Data', 'Vendedor', 'Cliente', 'Total', 'Forma Pagamento', 'Status'
        ])
        for s in qs:
            client_name = s.client.name if s.client else ('Avulsa' if s.is_walk_in else '-')
            writer.writerow([
                s.id,
                s.sale_date.strftime('%Y-%m-%d %H:%M') if s.sale_date else '',
                s.created_by.username if s.created_by else '',
                client_name,
                str(s.total),
                s.get_payment_method_display(),
                s.get_status_display(),
            ])
        response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="vendas_{start}_{end}.csv"'
        return response


class ProductsSoldExportCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _parse_params(request)
        category_id = request.query_params.get('category_id') or None
        order = request.query_params.get('order') or 'revenue'
        data = products_sold(start=start, end=end, category_id=category_id, order=order, limit=1000)
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            'ID Produto', 'Nome', 'Categoria', 'Qtd Vendida', 'Receita', 'Preço Médio', 'Lucro Est.', 'Participação %'
        ])
        for r in data:
            writer.writerow([
                r.get('product_id'),
                r.get('name'),
                r.get('category_name'),
                r.get('quantity_total'),
                r.get('revenue_total'),
                r.get('avg_price'),
                r.get('estimated_profit'),
                r.get('share_percent'),
            ])
        response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="produtos_vendidos_{start}_{end}.csv"'
        return response
