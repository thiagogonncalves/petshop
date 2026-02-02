"""
Serviço de criação de agendamentos com validação atômica.
"""
from datetime import datetime, date, time, timedelta

from django.db import transaction
from django.utils import timezone

from ..models import Appointment
from ..services.availability import get_available_slots, _get_config
from apps.services.models import Service
from apps.clients.models import Client
from apps.pets.models import Pet


def create_booking(
    client_id: int,
    pet_id: int,
    service_id: int,
    date_str: str,
    time_str: str,
    notes: str = '',
    created_via: str = 'client_self',
    created_by_user=None,
) -> Appointment:
    """
    Cria um agendamento com validação atômica.
    date_str: YYYY-MM-DD
    time_str: HH:MM
    Raises ValueError em caso de erro de validação.
    """
    config = _get_config()

    with transaction.atomic():
        try:
            client = Client.objects.get(pk=client_id, is_active=True)
        except Client.DoesNotExist:
            raise ValueError('Cliente não encontrado.')
        try:
            pet = Pet.objects.get(pk=pet_id, client=client)
        except Pet.DoesNotExist:
            raise ValueError('Animal não encontrado ou não pertence ao cliente.')
        try:
            service = Service.objects.select_for_update().get(pk=service_id, is_active=True)
        except Service.DoesNotExist:
            raise ValueError('Serviço não encontrado.')

        try:
            target_date = date.fromisoformat(date_str)
        except (ValueError, TypeError):
            raise ValueError('Data inválida.')
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError('Horário inválido.')
            slot_time = time(int(parts[0]), int(parts[1]), 0)
        except (ValueError, TypeError, IndexError):
            raise ValueError('Horário inválido.')

        available = get_available_slots(service_id, target_date)
        time_formatted = slot_time.strftime('%H:%M')
        if time_formatted not in available:
            raise ValueError(f'Horário {time_formatted} não está disponível para esta data.')

        start_at_naive = datetime.combine(target_date, slot_time)
        start_at = timezone.make_aware(start_at_naive)
        end_at = start_at + timedelta(minutes=service.duration_minutes)

        apt = Appointment(
            client=client,
            pet=pet,
            service=service,
            scheduled_date=start_at,
            start_at=start_at,
            end_at=end_at,
            status='scheduled',
            observations=notes or '',
            created_via=created_via,
            created_by=created_by_user,
        )
        apt.save()
        return apt
