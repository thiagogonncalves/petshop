"""
Crediário da Casa - Services for store credit (fiado) and installments
"""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from ..models import CreditAccount, CreditInstallment


def generate_installments(total, down_payment, n, first_due_date):
    """
    Generate installment plan for a credit account.

    total: Decimal - total amount of the sale
    down_payment: Decimal - amount paid at checkout (entrada)
    n: int - number of installments (2-12)
    first_due_date: date - due date for first installment

    Returns list of dicts: [{"number": 1, "due_date": date, "amount": Decimal}, ...]
    - Divide (total - down_payment) into n equal parts
    - Round each to 2 decimal places
    - Adjust cents difference on last installment
    """
    financed = total - down_payment
    if financed <= 0:
        return []
    if n < 1:
        return []

    base_amount = (financed / n).quantize(Decimal('0.01'))
    installments = []
    cumulative = Decimal('0.00')

    for i in range(1, n + 1):
        # Last installment gets the remainder to avoid rounding errors
        if i == n:
            amount = financed - cumulative
        else:
            amount = base_amount
            cumulative += amount

        # Calculate due date: monthly from first_due_date
        months_add = i - 1
        m = first_due_date.month - 1 + months_add
        y = first_due_date.year + m // 12
        m = m % 12 + 1
        last_day = monthrange(y, m)[1]
        day = min(first_due_date.day, last_day)
        due_date = date(y, m, day)

        installments.append({
            'number': i,
            'due_date': due_date,
            'amount': amount,
        })

    return installments


def mark_overdue_installments():
    """
    Mark pending installments as overdue when due_date < today.
    Call via cron/celery beat periodically.
    """
    today = date.today()
    CreditInstallment.objects.filter(
        status='pending',
        due_date__lt=today
    ).update(status='overdue')


def pay_installment(installment_id, amount, user, payment_method=None):
    """
    Mark an installment as paid.

    installment_id: int
    amount: Decimal - amount paid (default: full installment amount)
    user: User - who recorded the payment
    payment_method: str - forma de pagamento (cash, pix, debit_card, credit_card, bank_transfer)

    Returns (CreditInstallment, CreditAccount) or raises ValueError
    """
    valid_methods = ('cash', 'credit_card', 'debit_card', 'pix', 'bank_transfer')
    if payment_method and payment_method not in valid_methods:
        raise ValueError(f'Forma de pagamento inválida. Use: {", ".join(valid_methods)}.')

    with transaction.atomic():
        inst = CreditInstallment.objects.select_for_update().select_related(
            'credit_account'
        ).get(pk=installment_id)

        if inst.status == 'paid':
            raise ValueError('Parcela já está paga.')

        if inst.status == 'cancelled':
            raise ValueError('Parcela cancelada não pode ser paga.')

        amount = amount or inst.amount
        if amount < inst.amount:
            raise ValueError('Valor informado menor que o valor da parcela.')

        inst.status = 'paid'
        inst.paid_at = timezone.now()
        inst.paid_amount = amount
        inst.paid_by = user
        inst.payment_method = payment_method or 'cash'
        inst.save()

        # Recalculate credit account status
        account = inst.credit_account
        pending_count = account.installments.filter(
            status__in=['pending', 'overdue']
        ).count()

        if pending_count == 0:
            account.status = 'settled'
            account.save(update_fields=['status'])
            # Also update sale status
            account.sale.status = 'paid'
            account.sale.save(update_fields=['status'])

        return inst, account
