"""
Custom exception handlers for DRF
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'Erro na requisição',
            'details': response.data,
            'status_code': response.status_code
        }
        response.data = custom_response_data
    else:
        # Handle unexpected exceptions
        logger.exception(f'Unexpected error: {exc}')
        custom_response_data = {
            'error': True,
            'message': 'Erro interno do servidor',
            'details': str(exc),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response
