# Generated manually for Product.image

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_stock_smart_pricing_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Foto do produto'),
        ),
    ]
