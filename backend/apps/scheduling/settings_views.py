"""
Views para configurações de horário de funcionamento (admin).
"""
from datetime import datetime, date
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.users.permissions import IsAdmin

from .models import BusinessHoursConfig, BusinessHoursRule, BusinessClosure
from .serializers import BusinessHoursConfigSerializer, BusinessClosureSerializer


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def business_hours(request):
    """
    GET /api/settings/business-hours/ - retorna configuração
    PUT /api/settings/business-hours/ - atualiza configuração
    Body: {"slot_minutes": 30, "timezone": "America/Fortaleza", "rules": [{...}, ...]}
    """
    config = BusinessHoursConfig.objects.first()
    if request.method == 'GET':
        if not config:
            return Response({
                'slot_minutes': 30,
                'timezone': 'America/Fortaleza',
                'rules': [
                    {'weekday': i, 'is_open': i < 5, 'open_time': '08:00', 'close_time': '18:00', 'break_start': None, 'break_end': None}
                    for i in range(7)
                ],
            })
        serializer = BusinessHoursConfigSerializer(config)
        return Response(serializer.data)
    data = request.data
    if not config:
        config = BusinessHoursConfig.objects.create(
            slot_minutes=data.get('slot_minutes', 30),
            timezone=data.get('timezone', 'America/Fortaleza'),
        )
    else:
        config.slot_minutes = data.get('slot_minutes', config.slot_minutes)
        config.timezone = data.get('timezone', config.timezone)
        config.save()
    rules_data = data.get('rules', [])
    for r in rules_data:
        weekday = r.get('weekday')
        if weekday is None:
            continue
        rule, _ = BusinessHoursRule.objects.get_or_create(
            config=config,
            weekday=int(weekday),
            defaults={
                'is_open': r.get('is_open', True),
                'open_time': r.get('open_time'),
                'close_time': r.get('close_time'),
                'break_start': r.get('break_start'),
                'break_end': r.get('break_end'),
            },
        )
        rule.is_open = r.get('is_open', rule.is_open)
        if r.get('open_time') is not None:
            try:
                rule.open_time = datetime.strptime(r['open_time'], '%H:%M').time() if r.get('open_time') else None
            except (ValueError, TypeError):
                pass
        if r.get('close_time') is not None:
            try:
                rule.close_time = datetime.strptime(r['close_time'], '%H:%M').time() if r.get('close_time') else None
            except (ValueError, TypeError):
                pass
        if r.get('break_start'):
            try:
                rule.break_start = datetime.strptime(r['break_start'], '%H:%M').time()
            except (ValueError, TypeError):
                rule.break_start = None
        if r.get('break_end'):
            try:
                rule.break_end = datetime.strptime(r['break_end'], '%H:%M').time()
            except (ValueError, TypeError):
                rule.break_end = None
        rule.save()
    serializer = BusinessHoursConfigSerializer(config)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def closures_list(request):
    """
    GET /api/settings/closures/?start=&end=
    POST /api/settings/closures/
    Body: {"date": "2026-12-25", "reason": "Natal"}
    """
    if request.method == 'GET':
        qs = BusinessClosure.objects.all()
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        serializer = BusinessClosureSerializer(qs.order_by('date'), many=True)
        return Response(serializer.data)
    data = request.data
    date_str = data.get('date')
    reason = data.get('reason', '')
    if not date_str:
        return Response({'detail': 'date é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        target_date = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return Response({'detail': 'Data inválida.'}, status=status.HTTP_400_BAD_REQUEST)
    closure, created = BusinessClosure.objects.get_or_create(
        date=target_date,
        defaults={'reason': reason},
    )
    if not created:
        closure.reason = reason
        closure.save()
    serializer = BusinessClosureSerializer(closure)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def closure_delete(request, pk):
    """DELETE /api/settings/closures/{id}/"""
    try:
        closure = BusinessClosure.objects.get(pk=pk)
        closure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except BusinessClosure.DoesNotExist:
        return Response({'detail': 'Não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
