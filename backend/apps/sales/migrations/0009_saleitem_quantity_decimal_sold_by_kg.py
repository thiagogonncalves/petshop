# Generated migration - SaleItem quantity as Decimal, add sold_by_kg

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0008_creditinstallment_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleitem',
            name='sold_by_kg',
            field=models.BooleanField(default=False, verbose_name='Vendido por kg'),
        ),
        migrations.AlterField(
            model_name='saleitem',
            name='quantity',
            field=models.DecimalField(
                decimal_places=4,
                default=1,
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(Decimal('0.0001'))],
                verbose_name='Quantidade'
            ),
        ),
    ]
