"""
API pública de autoagendamento (sem autenticação).
"""
import logging
import re
from rest_framework import status

logger = logging.getLogger(__name__)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.clients.models import Client
from apps.clients.serializers import ClientSerializer
from apps.pets.models import Pet
from apps.pets.serializers import PetSerializer
from apps.services.models import Service
from apps.services.serializers import ServiceSerializer

from .models import Appointment
from .serializers import AppointmentSerializer
from .services.availability import get_available_slots, get_business_hours_metadata
from .services.booking import create_booking


def _cpf_digits(cpf_raw):
    return re.sub(r'[^0-9]', '', str(cpf_raw or ''))


@api_view(['POST'])
@permission_classes([AllowAny])
def check_cpf(request):
    """
    POST /api/public/booking/check-cpf/
    Body: {"cpf": "12345678901"}
    Response: {"exists": true, "client": {...}} ou {"exists": false}
    """
    cpf = _cpf_digits(request.data.get('cpf', ''))
    if len(cpf) != 11:
        return Response(
            {'detail': 'CPF inválido. Informe 11 dígitos.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    client = Client.objects.filter(is_active=True, document_type='cpf', document=cpf).first()
    if client:
        serializer = ClientSerializer(client)
        pets = client.pets.filter(is_active=True)
        pets_data = PetSerializer(pets, many=True).data
        return Response({'exists': True, 'client': serializer.data, 'pets': pets_data})
    return Response({'exists': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_client_pet(request):
    """
    POST /api/public/booking/register/
    Body: {"client": {"cpf":"...","name":"...","phone":"..."}, "pet": {"name":"...","species":"dog",...}}
    Response: {"client_id": N, "pet_id": M}
    """
    client_data = request.data.get('client', {})
    pet_data = request.data.get('pet', {})
    if not client_data or not pet_data:
        return Response(
            {'detail': 'Dados do cliente e do pet são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    cpf = _cpf_digits(client_data.get('cpf', ''))
    if len(cpf) != 11:
        return Response(
            {'detail': 'CPF inválido. Informe 11 dígitos.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if Client.objects.filter(document_type='cpf', document=cpf).exists():
        return Response(
            {'detail': 'Já existe cliente cadastrado com este CPF.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    name = (client_data.get('name') or '').strip()
    phone = (client_data.get('phone') or '').strip()
    if not name or not phone:
        return Response(
            {'detail': 'Nome e telefone do cliente são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    pet_name = (pet_data.get('name') or '').strip()
    pet_species = pet_data.get('species', 'dog')
    if not pet_name:
        return Response(
            {'detail': 'Nome do pet é obrigatório.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if pet_species not in ['dog', 'cat', 'bird', 'fish', 'reptile', 'rodent', 'other']:
        pet_species = 'dog'

    client = Client.objects.create(
        name=name,
        document_type='cpf',
        document=cpf,
        phone=phone,
        email=client_data.get('email') or '',
        is_active=True,
    )
    pet = Pet.objects.create(
        client=client,
        name=pet_name,
        species=pet_species,
        breed=pet_data.get('breed') or '',
        sex=pet_data.get('sex', 'unknown'),
        observations=pet_data.get('observations') or '',
        is_active=True,
    )
    return Response({'client_id': client.id, 'pet_id': pet.id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def available_slots(request):
    """
    GET /api/public/booking/available-slots?service_id=1&date=2026-02-15
    Response: {"slots": ["08:00","08:30",...], "meta": {...}}
    """
    service_id = request.query_params.get('service_id')
    date_str = request.query_params.get('date')
    if not service_id or not date_str:
        return Response(
            {'detail': 'service_id e date são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        from datetime import date
        target_date = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return Response(
            {'detail': 'Data inválida. Use formato YYYY-MM-DD.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    exclude_id = request.query_params.get('exclude_appointment_id')
    exclude_id = int(exclude_id) if exclude_id else None
    slots = get_available_slots(int(service_id), target_date, exclude_appointment_id=exclude_id)
    meta = get_business_hours_metadata()
    return Response({'slots': slots, 'meta': meta})


@api_view(['POST'])
@permission_classes([AllowAny])
def create_appointment(request):
    """
    POST /api/public/booking/appointments/
    Body: {"client_id": N, "pet_id": M, "service_id": K, "date": "2026-02-15", "time": "09:30", "notes": "..."}
    """
    data = request.data
    client_id = data.get('client_id')
    pet_id = data.get('pet_id')
    service_id = data.get('service_id')
    date_str = data.get('date')
    time_str = data.get('time')
    notes = data.get('notes', '')
    if not all([client_id, pet_id, service_id, date_str, time_str]):
        return Response(
            {'detail': 'client_id, pet_id, service_id, date e time são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        apt = create_booking(
            client_id=int(client_id),
            pet_id=int(pet_id),
            service_id=int(service_id),
            date_str=date_str,
            time_str=time_str,
            notes=notes,
            created_via='client_self',
            created_by_user=None,
        )
        serializer = AppointmentSerializer(apt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception('Erro ao criar agendamento público')
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_services(request):
    """GET /api/public/booking/services/ - lista serviços ativos."""
    services = Service.objects.filter(is_active=True).order_by('name')
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def my_appointments(request):
    """
    GET /api/public/booking/my-appointments/?cpf=12345678901
    Lista agendamentos do cliente por CPF.
    """
    cpf = _cpf_digits(request.query_params.get('cpf', ''))
    if len(cpf) != 11:
        return Response(
            {'detail': 'CPF inválido. Informe 11 dígitos.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    client = Client.objects.filter(document_type='cpf', document=cpf).first()
    if not client:
        return Response([])
    apts = Appointment.objects.filter(
        client=client
    ).exclude(status__in=['cancelled']).select_related('pet', 'service').order_by('-start_at')[:50]
    serializer = AppointmentSerializer(apts, many=True)
    return Response(serializer.data)
