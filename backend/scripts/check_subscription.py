#!/usr/bin/env python
"""
Diagnóstico e correção da assinatura.
Execute na raiz do projeto: python backend/manage.py shell < backend/scripts/check_subscription.py
"""
import os
import sys
import django

# Setup Django
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.users.models import CompanySettings
from apps.subscription.models import Subscription, Plan
from django.utils import timezone
from datetime import timedelta

cs = CompanySettings.objects.first()
print("=== CompanySettings.objects.first() ===")
print(f"  ID: {cs.id if cs else 'N/A'}, Nome: {cs.name if cs else '-'}")

print("\n=== Assinaturas ===")
for s in Subscription.objects.all().select_related('company', 'plan'):
    is_first = cs and s.company_id == cs.id
    mark = " <-- USADA pela API" if is_first else ""
    print(f"  id={s.id} company_id={s.company_id} status={s.status} can_write={s.can_write}{mark}")

if cs:
    sub = Subscription.objects.filter(company=cs).first()
    if sub:
        print("\n=== Aplicando correção (status=active) na assinatura correta ===")
        sub.status = 'active'
        sub.current_period_start = timezone.localdate()
        sub.current_period_end = timezone.localdate() + timedelta(days=30)
        sub.mp_payment_id = sub.mp_payment_id or 'test'
        sub.save()
        print(f"  OK! Assinatura id={sub.id} atualizada. Faça um REFRESH (F5) na página.")
    else:
        print("\n  Nenhuma assinatura encontrada para a empresa. Crie uma no admin.")
