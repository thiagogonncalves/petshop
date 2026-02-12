"""
Views de assinatura
"""
import hmac
import hashlib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from apps.users.models import CompanySettings
from .models import Subscription, SubscriptionStatus, Plan
from .services import create_mercado_pago_preference


def _validate_mp_webhook_signature(request):
    """
    Valida assinatura x-signature do Mercado Pago (HMAC-SHA256).
    Retorna True se válida ou se validação não configurada; False se inválida.
    """
    secret = getattr(settings, 'MERCADOPAGO_WEBHOOK_SECRET', '') or ''
    if not secret:
        return True  # Sem secret configurado, aceita

    x_sig = request.headers.get('x-signature') or request.META.get('HTTP_X_SIGNATURE')
    if not x_sig:
        return True  # notification_url pode não enviar assinatura; aceita para compatibilidade

    ts = v1_hash = None
    for part in x_sig.split(','):
        kv = part.split('=', 1)
        if len(kv) == 2:
            k, v = kv[0].strip(), kv[1].strip()
            if k == 'ts':
                ts = v
            elif k == 'v1':
                v1_hash = v

    if not ts or not v1_hash:
        return False

    data_id = request.GET.get('data.id') or (request.data or {}).get('data', {}).get('id') or ''
    if isinstance(data_id, (int, float)):
        data_id = str(int(data_id))
    if isinstance(data_id, str) and data_id.isalnum():
        data_id = data_id.lower()
    x_request_id = request.headers.get('x-request-id') or request.META.get('HTTP_X_REQUEST_ID') or ''

    parts = []
    if data_id:
        parts.append(f'id:{data_id}')
    if x_request_id:
        parts.append(f'request-id:{x_request_id}')
    parts.append(f'ts:{ts}')
    manifest = ';'.join(parts) + ';'

    expected = hmac.new(
        secret.encode('utf-8'),
        manifest.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, v1_hash)


def _get_subscription():
    company = CompanySettings.objects.first()
    if not company:
        return None
    sub, _ = Subscription.objects.get_or_create(
        company=company,
        defaults={
            'status': SubscriptionStatus.TRIAL,
            'trial_start': timezone.localdate(),
            'trial_end': timezone.localdate() + timedelta(days=7),
        }
    )
    return sub


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """
    GET /api/subscription/status
    Retorna status da assinatura: status, can_write, days_remaining_trial, plan, etc.
    """
    sub = _get_subscription()
    if not sub:
        return Response({
            'status': 'trial',
            'can_write': True,
            'days_remaining_trial': 7,
            'trial_end': None,
            'plan': None,
            'current_period_end': None,
        })

    plan_data = None
    if sub.plan:
        plan_data = {
            'id': sub.plan.id,
            'name': sub.plan.name,
            'price': str(sub.plan.price),
        }

    return Response({
        'status': sub.status,
        'can_write': sub.can_write,
        'days_remaining_trial': sub.days_remaining_trial,
        'trial_start': sub.trial_start.isoformat() if sub.trial_start else None,
        'trial_end': sub.trial_end.isoformat() if sub.trial_end else None,
        'plan': plan_data,
        'current_period_start': sub.current_period_start.isoformat() if sub.current_period_start else None,
        'current_period_end': sub.current_period_end.isoformat() if sub.current_period_end else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscription_pay(request):
    """
    POST /api/subscription/pay
    Gera cobrança Mercado Pago e retorna init_point (URL para checkout).
    """
    sub = _get_subscription()
    if not sub:
        return Response(
            {'detail': 'Empresa não configurada.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = create_mercado_pago_preference(sub)
    except ValueError as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({
        'init_point': result['init_point'],
        'preference_id': result['preference_id'],
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def mp_webhook(request):
    """
    Webhook Mercado Pago.
    POST /api/subscription/webhook
    Quando pagamento aprovado: status=ACTIVE, current_period_end.
    Valida x-signature se MERCADOPAGO_WEBHOOK_SECRET estiver configurado.
    """
    if not _validate_mp_webhook_signature(request):
        return Response({'ok': False, 'detail': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)

    # Mercado Pago envia: { "type": "payment", "data": { "id": "123" } }
    data = request.data or {}
    notif_type = data.get('type', '')
    payment_id = data.get('data', {}).get('id') or data.get('id')

    # Só processar notificações de pagamento (não preference)
    if notif_type and notif_type != 'payment':
        return Response({'ok': True})
    if not payment_id:
        return Response({'ok': True})

    try:
        import mercadopago
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        result = sdk.payment().get(payment_id)
    except Exception:
        return Response({'ok': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    payment = result.get('response', {})
    pay_status = payment.get('status')
    external_ref = payment.get('external_reference')

    if pay_status == 'approved' and external_ref:
        try:
            sub = Subscription.objects.get(id=external_ref)
        except Subscription.DoesNotExist:
            return Response({'ok': True})

        today = timezone.localdate()
        period_end = today + timedelta(days=30)  # 1 mês

        sub.status = SubscriptionStatus.ACTIVE
        sub.current_period_start = today
        sub.current_period_end = period_end
        sub.mp_payment_id = str(payment_id)
        sub.save(update_fields=[
            'status', 'current_period_start', 'current_period_end',
            'mp_payment_id', 'updated_at'
        ])

    return Response({'ok': True})
