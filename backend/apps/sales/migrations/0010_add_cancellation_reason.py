# Generated manually for cancellation_reason field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_saleitem_quantity_decimal_sold_by_kg'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='cancellation_reason',
            field=models.TextField(blank=True, verbose_name='Motivo do cancelamento'),
        ),
    ]
