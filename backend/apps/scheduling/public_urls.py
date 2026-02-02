"""
URLs públicas para autoagendamento (sem autenticação).
"""
from django.urls import path
from . import public_views

urlpatterns = [
    path('check-cpf/', public_views.check_cpf),
    path('register/', public_views.register_client_pet),
    path('available-slots/', public_views.available_slots),
    path('appointments/', public_views.create_appointment),
    path('services/', public_views.list_services),
    path('my-appointments/', public_views.my_appointments),
]
