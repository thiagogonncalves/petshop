"""
Aggregated queries for reports. All date filters use sale_date (timezone-aware).
Default: only paid sales; optional include/exclude cancelled.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import (
    Sum, Count, Avg, Q, F, Value, IntegerField, DecimalField,
    Case, When,
)
from django.db.models.functions import Coalesce, TruncDate, TruncDay
from django.utils import timezone

from apps.sales.models import Sale, SaleItem
from apps.products.models import Product, Category
from apps.services.models import Service
from apps.clients.models import Client
from apps.users.models import User


def get_sellers():
    """Users that have created at least one sale (for filter dropdown)."""
    rows = list(
        User.objects.filter(created_sales__isnull=False)
        .distinct()
        .values('id', 'username', 'first_name', 'last_name')
        .order_by('username')
    )
    for r in rows:
        name = f"{r.get('first_name') or ''} {r.get('last_name') or ''}".strip()
        r['name'] = name or r.get('username', '')
    return rows


def _parse_date(value, default):
    if value is None:
        return default
    if isinstance(value, date):
        return value
    from datetime import datetime
    return datetime.strptime(value, '%Y-%m-%d').date()


def _sales_queryset(start=None, end=None, user_id=None, client_id=None,
                     payment_method=None, status=None, exclude_cancelled=True):
    """Base Sale queryset with filters. Uses sale_date for period."""
    tz = timezone.get_current_timezone()
    qs = Sale.objects.all()
    if start is not None:
        qs = qs.filter(sale_date__date__gte=start)
    if end is not None:
        # end inclusive: up to end of day
        from datetime import datetime
        end_dt = timezone.make_aware(
            datetime.combine(end, datetime.max.time().replace(microsecond=0)),
            tz
        )
        qs = qs.filter(sale_date__lte=end_dt)
    if user_id:
        qs = qs.filter(created_by_id=user_id)
    if client_id:
        qs = qs.filter(client_id=client_id)
    if payment_method:
        qs = qs.filter(payment_method=payment_method)
    if status:
        qs = qs.filter(status=status)
    elif exclude_cancelled:
        qs = qs.exclude(status='cancelled')
    return qs


# ---------- Dashboard ----------
def dashboard_data(start, end, user_id=None, payment_method=None, status='paid'):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=30))
    sales_qs = _sales_queryset(
        start=start, end=end,
        user_id=user_id,
        payment_method=payment_method,
        status=status if status else None,
        exclude_cancelled=(status != 'cancelled' and not status),
    )
    agg = sales_qs.aggregate(
        total_count=Count('id'),
        total_revenue=Coalesce(Sum('total'), Decimal('0')),
        items_sold=Coalesce(
            Sum('items__quantity'),
            Value(0),
            output_field=IntegerField()
        ),
    )
    total_items = SaleItem.objects.filter(sale__in=sales_qs).aggregate(
        s=Coalesce(Sum('quantity'), Value(0), output_field=IntegerField())
    )['s'] or 0
    total_revenue = agg['total_revenue'] or Decimal('0')
    total_count = agg['total_count'] or 0
    ticket_avg = (total_revenue / total_count) if total_count else Decimal('0')

    # Lucro estimado: soma (quantity * (unit_price - cost)) para itens produto
    profit_agg = SaleItem.objects.filter(
        sale__in=sales_qs,
        item_type='product',
        product__isnull=False,
    ).annotate(
        cost=Coalesce(F('product__cost_price'), Decimal('0')),
        line_profit=F('unit_price') - F('cost'),
    ).aggregate(
        total_profit=Sum(F('line_profit') * F('quantity')),
    )
    estimated_profit = profit_agg['total_profit']

    # Vendas por dia (time series)
    daily = list(
        sales_qs.annotate(day=TruncDay('sale_date'))
        .values('day')
        .annotate(count=Count('id'), total=Coalesce(Sum('total'), Decimal('0')))
        .order_by('day')
    )
    for d in daily:
        d['date'] = d['day'].date().isoformat() if d.get('day') else None
        if 'day' in d:
            del d['day']

    # Por forma de pagamento
    by_payment = list(
        sales_qs.values('payment_method')
        .annotate(count=Count('id'), total=Coalesce(Sum('total'), Decimal('0')))
        .order_by('-total')
    )

    # Top 5 produtos (por receita)
    top_products = list(
        SaleItem.objects.filter(
            sale__in=sales_qs,
            item_type='product',
            product__isnull=False,
        )
        .values('product_id', 'product__name')
        .annotate(
            qty=Coalesce(Sum('quantity'), 0),
            revenue=Coalesce(Sum('total'), Decimal('0')),
        )
        .order_by('-revenue')[:5]
    )
    for p in top_products:
        p['name'] = p.pop('product__name')

    # Top 5 clientes (por receita; client not null)
    top_clients = list(
        sales_qs.filter(client__isnull=False)
        .values('client_id', 'client__name')
        .annotate(
            count=Count('id'),
            total=Coalesce(Sum('total'), Decimal('0')),
        )
        .order_by('-total')[:5]
    )
    for c in top_clients:
        c['name'] = c.pop('client__name')

    return {
        'total_sales': total_count,
        'total_revenue': total_revenue,
        'ticket_avg': ticket_avg,
        'total_items_sold': total_items,
        'estimated_profit': estimated_profit,
        'sales_by_day': daily,
        'sales_by_payment_method': by_payment,
        'top_5_products': top_products,
        'top_5_clients': top_clients,
        'period': {'start': start.isoformat(), 'end': end.isoformat()},
    }


# ---------- Relatório de vendas (lista paginada) ----------
def sales_report_queryset(start=None, end=None, user_id=None, client_id=None,
                          status=None, search=None, exclude_cancelled=True):
    qs = _sales_queryset(
        start=start, end=end,
        user_id=user_id, client_id=client_id,
        payment_method=None,
        status=status,
        exclude_cancelled=exclude_cancelled,
    ).select_related('client', 'created_by').order_by('-sale_date')
    if search:
        qs = qs.filter(
            Q(id__icontains=search) |
            Q(client__name__icontains=search) |
            Q(observations__icontains=search)
        )
    return qs


# ---------- Produtos vendidos ----------
def products_sold(start=None, end=None, category_id=None, order='revenue', limit=100):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=30))
    sales_qs = _sales_queryset(start=start, end=end, status='paid', exclude_cancelled=True)
    items_qs = SaleItem.objects.filter(
        sale__in=sales_qs,
        item_type='product',
        product__isnull=False,
    )
    if category_id:
        items_qs = items_qs.filter(product__category_id=category_id)
    profit_expr = ExpressionWrapper(
        (F('unit_price') - Coalesce(F('product__cost_price'), Decimal('0'))) * F('quantity'),
        output_field=DecimalField(),
    )
    agg = items_qs.values('product_id', 'product__name', 'product__category__name').annotate(
        quantity_total=Coalesce(Sum('quantity'), 0),
        revenue_total=Coalesce(Sum('total'), Decimal('0')),
        profit=Sum(profit_expr),
    ).annotate(
        avg_price=Case(
            When(quantity_total=0, then=Decimal('0')),
            default=F('revenue_total') / F('quantity_total'),
            output_field=DecimalField(),
        ),
    )
    total_revenue = items_qs.aggregate(s=Coalesce(Sum('total'), Decimal('0')))['s']
    order_field = {
        'qty': '-quantity_total',
        'revenue': '-revenue_total',
        'profit': '-profit',
    }.get(order, '-revenue_total')
    rows = list(agg.order_by(order_field)[:limit])
    result = []
    for row in rows:
        share = (float(row['revenue_total'] / total_revenue * 100)) if total_revenue else 0
        result.append({
            'product_id': row['product_id'],
            'name': row['product__name'],
            'category_name': row['product__category__name'],
            'quantity_total': row['quantity_total'],
            'revenue_total': row['revenue_total'],
            'avg_price': row['avg_price'],
            'estimated_profit': row['profit'],
            'share_percent': round(share, 2),
        })
    return result


# ---------- Ranking de vendedores ----------
def sales_ranking(start=None, end=None, order='revenue', limit=20):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=30))
    sales_qs = _sales_queryset(start=start, end=end, exclude_cancelled=True)
    by_user = list(
        sales_qs.values('created_by_id', 'created_by__username', 'created_by__first_name', 'created_by__last_name')
        .annotate(
            total_sales=Count('id'),
            total_revenue=Coalesce(Sum('total'), Decimal('0')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        )
    )
    # Items vendidos por vendedor (uma query)
    sale_ids = list(sales_qs.values_list('id', flat=True))
    items_by_user = {}
    if sale_ids:
        from django.db.models import Sum as S
        for row in SaleItem.objects.filter(sale_id__in=sale_ids).values('sale__created_by_id').annotate(s=S('quantity')):
            uid = row['sale__created_by_id']
            items_by_user[uid] = items_by_user.get(uid, 0) + row['s']
    result = []
    for row in by_user:
        uid = row['created_by_id']
        items = items_by_user.get(uid, 0)
        rev = row['total_revenue'] or Decimal('0')
        count = row['total_sales'] or 0
        ticket = (rev / count) if count else Decimal('0')
        cancel_count = row.get('cancelled') or 0
        cancel_rate = (cancel_count / count * 100) if count else 0
        name = row.get('created_by__username') or ''
        if row.get('created_by__first_name') or row.get('created_by__last_name'):
            name = f"{row.get('created_by__first_name') or ''} {row.get('created_by__last_name') or ''}".strip() or name
        result.append({
            'user_id': uid,
            'name': name,
            'username': row.get('created_by__username'),
            'total_sales': count,
            'items_sold': items,
            'revenue': rev,
            'ticket_avg': ticket,
            'cancellation_rate': round(cancel_rate, 2),
        })
    order_key = {'revenue': 'revenue', 'count': 'total_sales', 'items': 'items_sold'}.get(order, 'revenue')
    result.sort(key=lambda x: (float(x[order_key]) if isinstance(x[order_key], Decimal) else x[order_key]), reverse=True)
    return result[:limit]


# ---------- Estoque baixo / ruptura ----------
def low_stock(threshold=None):
    qs = Product.objects.filter(is_active=True)
    if threshold is not None:
        qs = qs.filter(stock_quantity__lte=threshold)
    else:
        qs = qs.filter(stock_quantity__lte=F('min_stock'))
    return list(
        qs.values('id', 'name', 'sku', 'stock_quantity', 'min_stock', 'category__name').annotate(
            suggestion=Case(
                When(min_stock__gt=0, then=F('min_stock') * 2 - F('stock_quantity')),
                default=Value(10),
                output_field=IntegerField(),
            ),
        ).order_by('stock_quantity')
    )


# ---------- Curva ABC (produtos) ----------
def abc_products(start=None, end=None, metric='revenue'):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=90))
    sales_qs = _sales_queryset(start=start, end=end, status='paid', exclude_cancelled=True)
    items_qs = SaleItem.objects.filter(
        sale__in=sales_qs,
        item_type='product',
        product__isnull=False,
    )
    if metric == 'qty':
        rows = list(
            items_qs.values('product_id', 'product__name')
            .annotate(value=Coalesce(Sum('quantity'), 0))
            .order_by('-value')
        )
    else:
        rows = list(
            items_qs.values('product_id', 'product__name')
            .annotate(value=Coalesce(Sum('total'), Decimal('0')))
            .order_by('-value')
        )
    total = sum(float(r['value']) for r in rows)
    cum = 0
    result = []
    for r in rows:
        cum += float(r['value'])
        pct = (cum / total * 100) if total else 0
        if pct <= 80:
            cls = 'A'
        elif pct <= 95:
            cls = 'B'
        else:
            cls = 'C'
        result.append({
            'product_id': r['product_id'],
            'name': r['product__name'],
            'value': r['value'],
            'cumulative_percent': round(pct, 2),
            'classification': cls,
        })
    return result


# ---------- Serviços mais vendidos ----------
def services_sold(start=None, end=None):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=30))
    sales_qs = _sales_queryset(start=start, end=end, status='paid', exclude_cancelled=True)
    rows = list(
        SaleItem.objects.filter(
            sale__in=sales_qs,
            item_type='service',
            service__isnull=False,
        )
        .values('service_id', 'service__name')
        .annotate(
            quantity=Coalesce(Sum('quantity'), 0),
            revenue=Coalesce(Sum('total'), Decimal('0')),
        )
        .order_by('-revenue')
    )
    return [{'service_id': r['service_id'], 'name': r['service__name'], 'quantity': r['quantity'], 'revenue': r['revenue']} for r in rows]


# ---------- Top clientes ----------
def top_clients(start=None, end=None, order='revenue', limit=20):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=30))
    sales_qs = _sales_queryset(start=start, end=end, status='paid', exclude_cancelled=True).filter(client__isnull=False)
    agg = list(
        sales_qs.values('client_id', 'client__name')
        .annotate(
            total_sales=Count('id'),
            total_revenue=Coalesce(Sum('total'), Decimal('0')),
        )
        .order_by('-total_revenue' if order == 'revenue' else '-total_sales')[:limit]
    )
    result = []
    for row in agg:
        count = row['total_sales']
        rev = row['total_revenue']
        result.append({
            'client_id': row['client_id'],
            'name': row['client__name'],
            'total_sales': count,
            'total_revenue': rev,
            'ticket_avg': (rev / count) if count else Decimal('0'),
        })
    return result


# ---------- Vendas por horário / dia da semana (heatmap) ----------
def sales_heatmap(start=None, end=None):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=90))
    sales_qs = _sales_queryset(start=start, end=end, status='paid', exclude_cancelled=True)
    from django.db.models.functions import ExtractHour, ExtractWeekDay
    rows = list(
        sales_qs.annotate(
            hour=ExtractHour('sale_date'),
            weekday=ExtractWeekDay('sale_date'),
        )
        .values('weekday', 'hour')
        .annotate(count=Count('id'), total=Coalesce(Sum('total'), Decimal('0')))
    )
    # weekday: 1=Sunday (Django), we can keep 1-7
    return {'data': rows, 'period': {'start': start.isoformat(), 'end': end.isoformat()}}


# ---------- Margem e lucro por produto ----------
def profit_by_product(start=None, end=None):
    end = _parse_date(end, timezone.now().date())
    start = _parse_date(start, end - timedelta(days=30))
    sales_qs = _sales_queryset(start=start, end=end, status='paid', exclude_cancelled=True)
    items_qs = SaleItem.objects.filter(
        sale__in=sales_qs,
        item_type='product',
        product__isnull=False,
    )
    rows = list(
        items_qs.values('product_id', 'product__name')
        .annotate(
            revenue=Coalesce(Sum('total'), Decimal('0')),
            cost=Coalesce(Sum(F('product__cost_price') * F('quantity')), Decimal('0')),
        )
        .annotate(
            profit=F('revenue') - F('cost'),
            margin=Case(
                When(revenue=0, then=Value(0)),
                default=(F('revenue') - F('cost')) / F('revenue') * 100,
                output_field=DecimalField(),
            ),
        )
        .order_by('-profit')
    )
    return [{
        'product_id': r['product_id'],
        'name': r['product__name'],
        'revenue': r['revenue'],
        'cost': r['cost'],
        'profit': r['profit'],
        'margin_percent': round(float(r['margin']), 2) if r['margin'] is not None else None,
    } for r in rows]
