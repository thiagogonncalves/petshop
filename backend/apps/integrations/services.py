"""
Integration services (mock implementations)
"""
import logging

logger = logging.getLogger(__name__)


class MercadoPagoService:
    """
    Mercado Pago payment integration service (mock)
    """
    
    @staticmethod
    def create_payment(amount, description, payment_method_id):
        """
        Create a payment in Mercado Pago
        Mock implementation - replace with real API calls
        """
        logger.info(f"Creating MercadoPago payment: {amount} - {description}")
        
        # Mock response
        return {
            'id': 'mock_payment_id',
            'status': 'approved',
            'status_detail': 'accredited',
            'transaction_amount': float(amount),
            'description': description,
            'payment_method_id': payment_method_id,
            'date_approved': None,
        }
    
    @staticmethod
    def get_payment(payment_id):
        """Get payment status from Mercado Pago"""
        logger.info(f"Getting MercadoPago payment: {payment_id}")
        
        # Mock response
        return {
            'id': payment_id,
            'status': 'approved',
            'transaction_amount': 100.00,
        }


class WhatsAppService:
    """
    WhatsApp integration service (mock)
    """
    
    @staticmethod
    def send_message(phone_number, message):
        """
        Send WhatsApp message
        Mock implementation - replace with real API calls (e.g., Twilio, WhatsApp Business API)
        """
        logger.info(f"Sending WhatsApp to {phone_number}: {message}")
        
        # Mock response
        return {
            'success': True,
            'message_id': 'mock_message_id',
            'status': 'sent'
        }
    
    @staticmethod
    def send_appointment_confirmation(appointment):
        """Send appointment confirmation via WhatsApp"""
        client = appointment.client
        message = f"Olá {client.name}! Seu agendamento para {appointment.pet.name} está confirmado para {appointment.scheduled_date.strftime('%d/%m/%Y %H:%M')}. Serviço: {appointment.service.name}."
        
        return WhatsAppService.send_message(client.phone, message)
    
    @staticmethod
    def send_appointment_reminder(appointment):
        """Send appointment reminder via WhatsApp"""
        client = appointment.client
        message = f"Lembrete: Seu agendamento para {appointment.pet.name} é amanhã às {appointment.scheduled_date.strftime('%H:%M')}."
        
        return WhatsAppService.send_message(client.phone, message)


class EmailService:
    """
    Email service (mock)
    """
    
    @staticmethod
    def send_email(to_email, subject, message, html_message=None):
        """
        Send email
        Mock implementation - replace with real SMTP or email service (e.g., SendGrid, AWS SES)
        """
        logger.info(f"Sending email to {to_email}: {subject}")
        
        # Mock response
        return {
            'success': True,
            'message_id': 'mock_email_id',
            'status': 'sent'
        }
    
    @staticmethod
    def send_receipt_email(receipt):
        """Send receipt via email"""
        sale = receipt.sale
        client = sale.client
        
        subject = f"Recibo #{receipt.receipt_number}"
        message = f"Olá {client.name}, segue seu recibo da compra realizada em {sale.sale_date.strftime('%d/%m/%Y')}. Valor total: R$ {sale.total:.2f}"
        
        if client.email:
            return EmailService.send_email(client.email, subject, message)
        
        return {'success': False, 'error': 'Cliente não possui e-mail cadastrado'}
    
    @staticmethod
    def send_invoice_email(invoice):
        """Send invoice via email"""
        sale = invoice.sale
        client = sale.client
        
        subject = f"Nota Fiscal #{invoice.invoice_number}"
        message = f"Olá {client.name}, segue sua nota fiscal da compra realizada em {sale.sale_date.strftime('%d/%m/%Y')}. Valor total: R$ {sale.total:.2f}"
        
        if client.email:
            return EmailService.send_email(client.email, subject, message)
        
        return {'success': False, 'error': 'Cliente não possui e-mail cadastrado'}
