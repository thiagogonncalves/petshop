# Generated manually for CompanySettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_role_and_custom_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='Nome da empresa')),
                ('cpf_cnpj', models.CharField(blank=True, max_length=20, verbose_name='CPF/CNPJ')),
                ('address', models.CharField(blank=True, max_length=300, verbose_name='Endereço')),
                ('address_number', models.CharField(blank=True, max_length=20, verbose_name='Número')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company/', verbose_name='Logo (PNG)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Dados da empresa',
                'verbose_name_plural': 'Dados da empresa',
            },
        ),
    ]
