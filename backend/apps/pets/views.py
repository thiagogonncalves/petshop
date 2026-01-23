"""
Pet views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Pet
from .serializers import PetSerializer
from .utils import generate_pet_card


class PetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Pet management
    """
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    filterset_fields = ['species', 'sex', 'is_active', 'client']
    search_fields = ['name', 'breed', 'client__name']

    @action(detail=True, methods=['get'])
    def card(self, request, pk=None):
        """Generate and return pet card PDF"""
        pet = self.get_object()
        
        try:
            pdf_buffer = generate_pet_card(pet)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="carteirinha_{pet.name}_{pet.id}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Erro ao gerar carteirinha: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
