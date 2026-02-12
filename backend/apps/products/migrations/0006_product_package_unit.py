# Migration: add Pacote (PKG) unit and units_per_package

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_product_unit_kg_price_per_kg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(
                choices=[('UN', 'Unidade'), ('KG', 'Quilograma (kg)'), ('PKG', 'Pacote')],
                default='UN',
                max_length=20,
                verbose_name='Unidade',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='units_per_package',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Quantas unidades formam 1 pacote (obrigatório quando unidade é Pacote)',
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Unidades por pacote',
            ),
        ),
    ]
