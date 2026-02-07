# Generated migration - add KG unit and price_per_kg

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(
                choices=[('UN', 'Unidade'), ('KG', 'Quilograma (kg)')],
                default='UN',
                max_length=20,
                verbose_name='Unidade'
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='price_per_kg',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))],
                verbose_name='Preço por kg (quando unidade é KG)'
            ),
        ),
    ]
