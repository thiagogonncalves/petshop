# Migration: add cash_received (valor recebido) to Sale

from decimal import Decimal
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0012_add_change_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='cash_received',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Valor recebido em dinheiro (quando há troco)',
                max_digits=10,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))],
                verbose_name='Valor recebido',
            ),
        ),
    ]
