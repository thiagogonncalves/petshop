"""
Product and pricing tests.
"""
from decimal import Decimal
from django.test import TestCase
from .models import Category, Product
from .services import calculate_sale_price


class PricingServiceTest(TestCase):
    """Test calculate_sale_price."""

    def test_calculate_sale_price_basic(self):
        self.assertEqual(
            calculate_sale_price(Decimal('100'), Decimal('30')),
            Decimal('130.00')
        )

    def test_calculate_sale_price_zero_margin(self):
        self.assertEqual(
            calculate_sale_price(Decimal('50.50'), Decimal('0')),
            Decimal('50.50')
        )

    def test_calculate_sale_price_rounding(self):
        # 10 * 1.33 = 13.30 (half up)
        self.assertEqual(
            calculate_sale_price(Decimal('10'), Decimal('33')),
            Decimal('13.30')
        )

    def test_calculate_sale_price_minimum(self):
        self.assertGreaterEqual(
            calculate_sale_price(Decimal('0'), Decimal('50')),
            Decimal('0.01')
        )


class ProductPricingTest(TestCase):
    """Test Product recalculate_sale_price and price_manually_set."""

    def setUp(self):
        self.category = Category.objects.create(name='Test', description='Test')

    def test_recalculate_sale_price_from_margin(self):
        p = Product.objects.create(
            name='Prod',
            category=self.category,
            cost_price=Decimal('100'),
            profit_margin=Decimal('25'),
            sale_price=Decimal('100'),
            price_manually_set=False,
            stock_quantity=0,
            min_stock=0,
        )
        self.assertEqual(p.sale_price, Decimal('125.00'))

    def test_manual_price_not_recalculated(self):
        p = Product.objects.create(
            name='Prod',
            category=self.category,
            cost_price=Decimal('100'),
            profit_margin=Decimal('25'),
            sale_price=Decimal('200'),
            price_manually_set=True,
            stock_quantity=0,
            min_stock=0,
        )
        self.assertEqual(p.sale_price, Decimal('200'))
