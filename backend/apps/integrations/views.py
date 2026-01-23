"""
Integration views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import MercadoPagoService, WhatsAppService, EmailService
from apps.sales.models import Sale, Receipt, Invoice
from apps.scheduling.models import Appointment


class IntegrationViewSet(viewsets.ViewSet):
    """
    ViewSet for Integrations
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def mercado_pago_payment(self, request):
        """Process payment via Mercado Pago"""
        sale_id = request.data.get('sale_id')
        payment_method_id = request.data.get('payment_method_id', 'pix')
        
        try:
            sale = Sale.objects.get(id=sale_id)
            
            result = MercadoPagoService.create_payment(
                amount=sale.total,
                description=f"Venda #{sale.id}",
                payment_method_id=payment_method_id
            )
            
            if result['status'] == 'approved':
                sale.status = 'paid'
                sale.save()
            
            return Response(result)
        except Sale.DoesNotExist:
            return Response(
                {'error': 'Venda não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def send_whatsapp(self, request):
        """Send WhatsApp message"""
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        
        if not phone_number or not message:
            return Response(
                {'error': 'phone_number e message são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = WhatsAppService.send_message(phone_number, message)
        return Response(result)

    @action(detail=False, methods=['post'])
    def send_appointment_confirmation(self, request):
        """Send appointment confirmation via WhatsApp"""
        appointment_id = request.data.get('appointment_id')
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            result = WhatsAppService.send_appointment_confirmation(appointment)
            return Response(result)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Agendamento não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def send_receipt_email(self, request):
        """Send receipt via email"""
        receipt_id = request.data.get('receipt_id')
        
        try:
            receipt = Receipt.objects.get(id=receipt_id)
            result = EmailService.send_receipt_email(receipt)
            return Response(result)
        except Receipt.DoesNotExist:
            return Response(
                {'error': 'Recibo não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def send_invoice_email(self, request):
        """Send invoice via email"""
        invoice_id = request.data.get('invoice_id')
        
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            result = EmailService.send_invoice_email(invoice)
            return Response(result)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
