"""
Aggregated queries for reports. All date filters use sale_date (timezone-aware).
Default: only paid sales; optional include/exclude cancelled.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import (
    Sum, Count, Avg, Q, F, Value, IntegerField, DecimalField,
    Case, When, ExpressionWrapper,
)
from django.db.models.functions import Coalesce, TruncDate, TruncDay
from django.utils import timezone

from apps.sales.models import Sale, SaleItem, CreditAccount, CreditInstallment
from apps.products.models import Product, Category
from apps.services.models import Service
from apps.clients.models import Client
from apps.users.models import User
from apps.scheduling.models import Appointment


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
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    if isinstance(value, date):
        return value
    from datetime import datetime
    try:
        return datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return default


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


# ---------- Dashboard resumido (único endpoint agregado) ----------
def get_dashboard_summary(target_date=None):
    """
    Retorna todos os dados do dashboard em uma única chamada.
    GET /api/reports/dashboard-summary/?date=YYYY-MM-DD
    """
    today = _parse_date(target_date, timezone.now().date())
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)
    seven_days_ago = today - timedelta(days=7)
    inactive_days = 60  # clientes inativos: sem compra/agendamento há 60 dias
    low_stock_threshold = 5

    tz = timezone.get_current_timezone()

    # --- KPIs ---
    sales_paid_qs = Sale.objects.filter(
        status__in=['paid', 'credit_open'],
    ).exclude(status='cancelled')

    # Vendas hoje
    from datetime import datetime
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()), tz)
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time().replace(microsecond=0)), tz)
    yesterday_start = timezone.make_aware(datetime.combine(yesterday, datetime.min.time()), tz)
    yesterday_end = timezone.make_aware(datetime.combine(yesterday, datetime.max.time().replace(microsecond=0)), tz)

    sales_today_agg = sales_paid_qs.filter(sale_date__gte=today_start, sale_date__lte=today_end).aggregate(
        total=Coalesce(Sum('total'), Decimal('0'))
    )
    sales_yesterday_agg = sales_paid_qs.filter(sale_date__gte=yesterday_start, sale_date__lte=yesterday_end).aggregate(
        total=Coalesce(Sum('total'), Decimal('0'))
    )
    sales_today = sales_today_agg['total'] or Decimal('0')
    sales_yesterday = sales_yesterday_agg['total'] or Decimal('0')

    sales_today_change_pct = 0
    if sales_yesterday and sales_yesterday > 0:
        sales_today_change_pct = float((sales_today - sales_yesterday) / sales_yesterday * 100)

    # Vendas no mês
    month_end = timezone.make_aware(datetime.combine(today, datetime.max.time().replace(microsecond=0)), tz)
    sales_month_agg = sales_paid_qs.filter(
        sale_date__gte=timezone.make_aware(datetime.combine(month_start, datetime.min.time()), tz),
        sale_date__lte=month_end,
    ).aggregate(total=Coalesce(Sum('total'), Decimal('0')))
    sales_month = sales_month_agg['total'] or Decimal('0')
    sales_month_goal = None  # opcional, pode vir de config

    # Atendimentos hoje
    today_appts = Appointment.objects.filter(
        start_at__date=today,
    ).exclude(status__in=['cancelled', 'no_show'])
    appts_total = today_appts.count()
    appts_done = today_appts.filter(status__in=['completed', 'done']).count()

    # Crediário em aberto (valor total de parcelas pendentes/overdue)
    credit_open_total = CreditInstallment.objects.filter(
        credit_account__status='open',
        status__in=['pending', 'overdue'],
    ).aggregate(t=Coalesce(Sum('amount'), Decimal('0')))['t'] or Decimal('0')
    credit_overdue_count = CreditInstallment.objects.filter(
        credit_account__status='open',
        status__in=['pending', 'overdue'],
        due_date__lt=today,
    ).count()

    kpis = {
        'sales_today': float(sales_today),
        'sales_yesterday': float(sales_yesterday),
        'sales_today_change_pct': round(sales_today_change_pct, 1),
        'sales_month': float(sales_month),
        'sales_month_goal': float(sales_month_goal) if sales_month_goal else None,
        'appointments_today_total': appts_total,
        'appointments_today_done': appts_done,
        'credit_open_total': float(credit_open_total),
        'credit_overdue_count': credit_overdue_count,
    }

    # --- Agenda do dia ---
    schedule_qs = Appointment.objects.filter(
        start_at__date=today,
    ).exclude(status__in=['cancelled', 'no_show']).select_related('client', 'pet', 'service').order_by('start_at')
    today_schedule = []
    for apt in schedule_qs:
        start_at = apt.start_at
        time_str = start_at.strftime('%H:%M') if start_at else ''
        today_schedule.append({
            'id': apt.id,
            'time': time_str,
            'client': apt.client.name if apt.client else '-',
            'pet': apt.pet.name if apt.pet else '-',
            'service': apt.service.name if apt.service else '-',
            'status': apt.status,
            'status_display': apt.get_status_display(),
        })

    # --- Alertas ---
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=low_stock_threshold,
    ).order_by('stock_quantity')[:10].values('id', 'name', 'stock_quantity')
    low_stock_list = [
        {'product_id': p['id'], 'name': p['name'], 'balance': p['stock_quantity']}
        for p in low_stock_products
    ]

    credit_due_list = []
    overdue_installs = CreditInstallment.objects.filter(
        credit_account__status='open',
        status__in=['pending', 'overdue'],
        due_date__lte=today + timedelta(days=7),
    ).select_related('credit_account__client').order_by('due_date')[:10]
    for inst in overdue_installs:
        client_name = inst.credit_account.client.name if inst.credit_account.client else '-'
        credit_due_list.append({
            'installment_id': inst.id,
            'credit_id': inst.credit_account_id,
            'client': client_name,
            'amount': float(inst.amount),
            'due_date': inst.due_date.isoformat(),
            'status': 'OVERDUE' if inst.due_date < today else 'DUE',
        })

    alerts = {
        'low_stock': low_stock_list,
        'credit_due': credit_due_list,
    }

    # --- Top clientes do mês ---
    month_sales_qs = sales_paid_qs.filter(
        sale_date__gte=timezone.make_aware(datetime.combine(month_start, datetime.min.time()), tz),
        sale_date__lte=month_end,
        client__isnull=False,
    )
    top_clients_month = list(
        month_sales_qs.values('client_id', 'client__name')
        .annotate(
            revenue=Coalesce(Sum('total'), Decimal('0')),
            visits=Count('id'),
        )
        .order_by('-revenue')[:5]
    )
    customers_top = [
        {
            'client_id': r['client_id'],
            'name': r['client__name'],
            'revenue': float(r['revenue']),
            'visits': r['visits'],
        }
        for r in top_clients_month
    ]

    # --- Clientes inativos (sem venda nem agendamento há 60+ dias) ---
    from django.db.models import Max
    inactive_cutoff = timezone.make_aware(datetime.combine(today - timedelta(days=inactive_days), datetime.min.time()), tz)
    clients_with_recent_sale = set(
        Sale.objects.filter(sale_date__gte=inactive_cutoff, client__isnull=False).values_list('client_id', flat=True)
    )
    clients_with_recent_apt = set(
        Appointment.objects.filter(start_at__gte=inactive_cutoff).values_list('client_id', flat=True)
    )
    clients_with_recent = clients_with_recent_sale | clients_with_recent_apt
    inactive_clients_qs = Client.objects.filter(is_active=True).exclude(id__in=clients_with_recent)
    last_sale_map = dict(
        Sale.objects.filter(client__isnull=False)
        .values('client_id')
        .annotate(d=Max('sale_date'))
        .values_list('client_id', 'd')
    )
    last_apt_map = dict(
        Appointment.objects.values('client_id')
        .annotate(d=Max('start_at'))
        .values_list('client_id', 'd')
    )
    inactive_list = []
    for c in inactive_clients_qs[:15]:
        ls = last_sale_map.get(c.id)
        la = last_apt_map.get(c.id)
        candidates = [x for x in [ls, la] if x is not None]
        last_dt = max(candidates) if candidates else None
        if last_dt:
            last_date = last_dt.date() if hasattr(last_dt, 'date') else last_dt
            days_inactive = (today - last_date).days
            inactive_list.append({
                'client_id': c.id,
                'name': c.name,
                'last_visit': last_date.isoformat(),
                'days_inactive': days_inactive,
            })
    inactive_list.sort(key=lambda x: x['days_inactive'], reverse=True)
    inactive_list = inactive_list[:5]

    customers = {
        'top_clients_month': customers_top,
        'inactive_clients': inactive_list,
    }

    # --- Gráficos ---
    seven_days_start = timezone.make_aware(datetime.combine(seven_days_ago, datetime.min.time()), tz)
    sales_7d_qs = sales_paid_qs.filter(
        sale_date__gte=seven_days_start,
        sale_date__lte=today_end,
    )
    sales_7d = list(
        sales_7d_qs.annotate(day=TruncDay('sale_date'))
        .values('day')
        .annotate(value=Coalesce(Sum('total'), Decimal('0')))
        .order_by('day')
    )
    sales_7d_by_date = {r['day'].date(): r['value'] for r in sales_7d if r.get('day')}
    sales_last_7_days = []
    for d in range(8):
        dt = seven_days_ago + timedelta(days=d)
        if dt <= today:
            sales_last_7_days.append({
                'date': dt.isoformat(),
                'value': float(sales_7d_by_date.get(dt, Decimal('0'))),
            })

    sale_ids_7d = list(sales_7d_qs.values_list('id', flat=True))
    top_products = list(
        SaleItem.objects.filter(
            sale_id__in=sale_ids_7d,
            item_type='product',
            product__isnull=False,
        )
        .values('product_id', 'product__name')
        .annotate(
            qty=Coalesce(Sum('quantity'), 0),
            revenue=Coalesce(Sum('total'), Decimal('0')),
        )
        .order_by('-qty')[:5]
    ) if sale_ids_7d else []
    charts_top_products = [
        {
            'product_id': r['product_id'],
            'name': r['product__name'],
            'qty': r['qty'],
            'revenue': float(r['revenue']),
        }
        for r in top_products
    ]

    charts = {
        'sales_last_7_days': sales_last_7_days,
        'top_products': charts_top_products,
    }

    # --- Insights ---
    insights = []
    if today_schedule:
        from collections import Counter
        hours = [a['time'].split(':')[0] for a in today_schedule if a.get('time')]
        if hours:
            most_hour = Counter(hours).most_common(1)[0][0]
            insights.append(f'Horário mais movimentado hoje: {most_hour}h–{int(most_hour)+1}h')
    if charts_top_products:
        insights.append(f'Produto mais vendido na semana: {charts_top_products[0]["name"]}')
    if credit_overdue_count > 0:
        insights.append(f'Existem {credit_overdue_count} parcela(s) vencida(s) no crediário.')
    if not insights:
        insights.append('Nenhum insight específico para hoje.')

    return {
        'kpis': kpis,
        'today_schedule': today_schedule,
        'alerts': alerts,
        'customers': customers,
        'charts': charts,
        'insights': insights,
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
