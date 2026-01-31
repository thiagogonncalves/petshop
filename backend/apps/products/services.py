"""
Product services: pricing and stock balance.
"""
from decimal import Decimal, ROUND_HALF_UP


def calculate_sale_price(cost_price: Decimal, profit_margin_percent: Decimal) -> Decimal:
    """
    sale_price = cost_price * (1 + profit_margin / 100).
    Uses quantize(0.01, ROUND_HALF_UP).
    """
    if cost_price is None or cost_price < 0:
        cost_price = Decimal('0.00')
    if profit_margin_percent is None or profit_margin_percent < 0:
        profit_margin_percent = Decimal('0.00')
    result = (cost_price * (Decimal('1') + profit_margin_percent / Decimal('100'))).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    return max(result, Decimal('0.01'))
