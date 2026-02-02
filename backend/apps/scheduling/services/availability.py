"""
Serviço de disponibilidade de horários para agendamento.
Timezone: America/Fortaleza
"""
from datetime import date, time, datetime, timedelta
from typing import List, Optional

import pytz
from django.db.models import Q

from ..models import Appointment, BusinessHoursConfig, BusinessHoursRule, BusinessClosure
from apps.services.models import Service


def _get_config() -> Optional[BusinessHoursConfig]:
    """Retorna a configuração de horário (singleton)."""
    return BusinessHoursConfig.objects.first()


def _get_tz():
    """Retorna o timezone do pet shop."""
    config = _get_config()
    tz_name = config.timezone if config else 'America/Fortaleza'
    return pytz.timezone(tz_name)


def _get_rule_for_weekday(weekday: int) -> Optional[BusinessHoursRule]:
    """Retorna a regra para o dia da semana (0=Seg...6=Dom)."""
    config = _get_config()
    if not config:
        return None
    return config.rules.filter(weekday=weekday).first()


def _is_date_closed(target_date: date) -> bool:
    """Verifica se a data está em um fechamento (feriado, folga)."""
    return BusinessClosure.objects.filter(date=target_date).exists()


def _get_open_slots_for_day(
    target_date: date,
    slot_minutes: int,
    open_time: time,
    close_time: time,
    break_start: Optional[time] = None,
    break_end: Optional[time] = None,
) -> List[time]:
    """
    Gera lista de horários de início de slots para um dia.
    Ex: 08:00, 08:30, 09:00 ... até close_time - slot_minutes
    Exclui slots que caem no intervalo de pausa.
    """
    slots = []
    current = datetime.combine(target_date, open_time)
    close_dt = datetime.combine(target_date, close_time)
    delta = timedelta(minutes=slot_minutes)

    if break_start and break_end:
        break_start_dt = datetime.combine(target_date, break_start)
        break_end_dt = datetime.combine(target_date, break_end)

    while current + delta <= close_dt:
        slot_time = current.time()
        # Excluir slots que se sobrepõem à pausa
        if break_start and break_end:
            slot_end = (current + delta).time()
            if slot_time < break_end and slot_end > break_start:
                current += delta
                continue
        slots.append(slot_time)
        current += delta

    return slots


def get_available_slots(
    service_id: int,
    target_date: date,
    exclude_appointment_id: Optional[int] = None,
) -> List[str]:
    """
    Retorna horários disponíveis (strings HH:MM) para um serviço em uma data.
    Considera:
    - Dias da semana abertos
    - Horário de funcionamento
    - Pausa/intervalo
    - Feriados/fechamentos
    - Conflitos com agendamentos existentes (considerando duração do serviço)
    """
    try:
        service = Service.objects.get(pk=service_id, is_active=True)
    except Service.DoesNotExist:
        return []

    config = _get_config()
    slot_minutes = config.slot_minutes if config else 30
    duration_minutes = service.duration_minutes

    weekday = target_date.weekday()  # 0=Segunda, 6=Domingo
    rule = _get_rule_for_weekday(weekday)

    if _is_date_closed(target_date):
        return []

    if not rule or not rule.is_open or not rule.open_time or not rule.close_time:
        return []

    all_slots = _get_open_slots_for_day(
        target_date,
        slot_minutes,
        rule.open_time,
        rule.close_time,
        rule.break_start,
        rule.break_end,
    )

    tz = _get_tz()
    # Horários em que o serviço terminaria (start + duration)
    # Um slot é válido se start + duration <= próximo slot ou close_time
    service_slots_needed = max(1, (duration_minutes + slot_minutes - 1) // slot_minutes)

    # Buscar agendamentos do dia (não cancelados, não no_show)
    busy_qs = Appointment.objects.filter(
        start_at__date=target_date,
    ).exclude(status__in=['cancelled', 'no_show'])
    if exclude_appointment_id:
        busy_qs = busy_qs.exclude(pk=exclude_appointment_id)
    busy_appointments = busy_qs

    available = []
    for slot_time in all_slots:
        slot_start = datetime.combine(target_date, slot_time).replace(tzinfo=tz)
        slot_end = slot_start + timedelta(minutes=duration_minutes)

        # Verificar se cabe no horário de fechamento
        close_dt = datetime.combine(target_date, rule.close_time).replace(tzinfo=tz)
        if slot_end > close_dt:
            continue

        # Verificar pausa
        if rule.break_start and rule.break_end:
            break_start_dt = datetime.combine(target_date, rule.break_start).replace(tzinfo=tz)
            break_end_dt = datetime.combine(target_date, rule.break_end).replace(tzinfo=tz)
            if slot_start < break_end_dt and slot_end > break_start_dt:
                continue

        # Verificar conflito com agendamentos
        has_conflict = False
        for apt in busy_appointments:
            apt_start = apt.start_at
            apt_end = apt.end_at
            if apt_start.tzinfo is None and hasattr(apt_start, 'replace'):
                apt_start = tz.localize(apt_start.replace(tzinfo=None))
            elif apt_start.tzinfo:
                apt_start = apt_start.astimezone(tz)
            if apt_end.tzinfo is None and hasattr(apt_end, 'replace'):
                apt_end = tz.localize(apt_end.replace(tzinfo=None))
            elif apt_end.tzinfo:
                apt_end = apt_end.astimezone(tz)
            if slot_start < apt_end and slot_end > apt_start:
                has_conflict = True
                break

        if not has_conflict:
            available.append(slot_time.strftime('%H:%M'))

    return available


def get_business_hours_metadata() -> dict:
    """Retorna metadados da configuração (slot_minutes, timezone, etc.)."""
    config = _get_config()
    if not config:
        return {
            'slot_minutes': 30,
            'timezone': 'America/Fortaleza',
            'rules': [],
        }
    rules = []
    for r in config.rules.order_by('weekday'):
        rules.append({
            'weekday': r.weekday,
            'is_open': r.is_open,
            'open_time': r.open_time.strftime('%H:%M') if r.open_time else None,
            'close_time': r.close_time.strftime('%H:%M') if r.close_time else None,
            'break_start': r.break_start.strftime('%H:%M') if r.break_start else None,
            'break_end': r.break_end.strftime('%H:%M') if r.break_end else None,
        })
    return {
        'slot_minutes': config.slot_minutes,
        'timezone': config.timezone,
        'rules': rules,
    }
