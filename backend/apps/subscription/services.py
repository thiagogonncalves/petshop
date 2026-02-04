"""
Serviços de assinatura e Mercado Pago
"""
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Subscription, SubscriptionStatus, Plan

logger = logging.getLogger(__name__)


def create_mercado_pago_preference(subscription):
    """
    Gera preferência de pagamento no Mercado Pago (Checkout Pro).
    Retorna dict com init_point e preference_id ou None em caso de erro.
    Em caso de erro, levanta ValueError com mensagem útil.
    """
    access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
    if not access_token:
        raise ValueError('MERCADOPAGO_ACCESS_TOKEN não configurado no .env')

    try:
        import mercadopago
        sdk = mercadopago.SDK(access_token)
    except ImportError:
        raise ValueError('Pacote mercadopago não instalado. Execute: pip install mercadopago')

    plan = subscription.plan
    if not plan:
        plan = Plan.objects.filter(is_active=True).first()
        if not plan:
            raise ValueError('Nenhum plano ativo cadastrado. Configure um plano no admin.')

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    webhook_url = getattr(settings, 'MERCADOPAGO_WEBHOOK_URL', '')

    success_url = f'{frontend_url}/admin/plan'
    preference_data = {
        'items': [{
            'title': f'Plano {plan.name} - Mensal',
            'quantity': 1,
            'unit_price': float(plan.price),
            'currency_id': 'BRL',
        }],
        'payer': {
            'email': 'cliente@exemplo.com',
        },
        'external_reference': str(subscription.id),
        'back_urls': {
            'success': success_url,
            'failure': success_url,
            'pending': success_url,
        },
    }

    if webhook_url:
        preference_data['notification_url'] = webhook_url.rstrip('/')

    try:
        result = sdk.preference().create(preference_data)
    except Exception as e:
        logger.exception('Erro ao criar preferência Mercado Pago')
        raise ValueError(f'Erro Mercado Pago: {str(e)}')

    response = result.get('response', {})
    if 'id' in response:
        pref = response
        subscription.mp_preference_id = pref.get('id', '')
        subscription.save(update_fields=['mp_preference_id', 'updated_at'])
        return {
            'init_point': pref.get('init_point'),
            'preference_id': pref.get('id'),
        }

    err_msg = response.get('message', 'Resposta inválida da API')
    err_cause = response.get('cause', [{}])
    if err_cause and isinstance(err_cause, list) and err_cause:
        first = err_cause[0] if err_cause else {}
        desc = first.get('description', first.get('message', ''))
        if desc:
            err_msg = f'{err_msg}: {desc}'
    raise ValueError(f'Mercado Pago: {err_msg}')
