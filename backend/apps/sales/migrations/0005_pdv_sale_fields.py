# Generated manually for PDV module

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_alter_sale_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='is_walk_in',
            field=models.BooleanField(default=False, verbose_name='Venda avulsa'),
        ),
        migrations.AddField(
            model_name='sale',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, verbose_name='CPF (auditoria avulsa)'),
        ),
    ]
