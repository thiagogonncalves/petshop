"""
Middleware que bloqueia requisições de escrita quando assinatura expirada.
Regra: GET sempre permitido. POST/PUT/PATCH/DELETE bloqueados se trial expirado e status != ACTIVE.
"""
import re
from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from apps.users.models import CompanySettings
from .models import Subscription, SubscriptionStatus


# Rotas que sempre permitem escrita (independente da assinatura)
# Login, token refresh e pagamento devem funcionar mesmo com trial expirado
ALLOWED_PATHS = [
    r'^/api/auth/users/login/?$',
    r'^/api/auth/token/refresh/?$',
    r'^/api/auth/first-login/?$',
    r'^/api/subscription/pay/?$',
    r'^/api/subscription/webhook/?$',
    r'^/api/subscription/status/?$',  # GET já permitido; POST se existir
]
ALLOWED_PATHS_RE = [re.compile(p) for p in ALLOWED_PATHS]

# Métodos considerados "leitura" - sempre permitidos
READ_METHODS = {'GET', 'HEAD', 'OPTIONS'}


def _path_allowed(path):
    for pattern in ALLOWED_PATHS_RE:
        if pattern.match(path):
            return True
    return False


def _get_subscription():
    """Obtém a assinatura da empresa (singleton). Cria trial se não existir."""
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


class SubscriptionMiddleware:
    """
    Bloqueia requisições de escrita (POST, PUT, PATCH, DELETE) quando:
    - status != ACTIVE
    - E hoje > trial_end
    Exceto nas rotas permitidas (login, pagamento, webhook).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        method = request.method.upper()

        # Só aplica a rotas /api/
        if not path.startswith('/api/'):
            return self.get_response(request)

        # Método de leitura: sempre permite
        if method in READ_METHODS:
            return self.get_response(request)

        # Rotas explícitas permitidas
        if _path_allowed(path):
            return self.get_response(request)

        # Verificar assinatura
        try:
            sub = _get_subscription()
        except Exception:
            return self.get_response(request)

        if not sub:
            return self.get_response(request)

        if sub.can_write:
            return self.get_response(request)

        # Bloqueado: trial expirado e não ativo
        return JsonResponse(
            {
                'error': True,
                'detail': 'subscription_expired',
                'message': 'Sua assinatura expirou. Renove seu plano para continuar editando.',
            },
            status=403,
        )
