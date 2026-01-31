# Generated for reports module performance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_pdv_sale_fields'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(fields=['created_by'], name='sales_sale_created_8a0b0d_idx'),
        ),
        migrations.AddIndex(
            model_name='saleitem',
            index=models.Index(fields=['sale'], name='sales_saleitem_sale_id_9c2a1e_idx'),
        ),
        migrations.AddIndex(
            model_name='saleitem',
            index=models.Index(fields=['product'], name='sales_saleitem_product_7d4f2a_idx'),
        ),
    ]
