# Generated manually for Role and User.custom_role

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('code', models.SlugField(max_length=50, unique=True, verbose_name='Código')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Perfil',
                'verbose_name_plural': 'Perfis',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_code', models.CharField(max_length=50)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='users.role')),
            ],
            options={
                'verbose_name': 'Permissão do perfil',
                'verbose_name_plural': 'Permissões do perfil',
                'unique_together': {('role', 'permission_code')},
            },
        ),
        migrations.AddField(
            model_name='user',
            name='custom_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='users.role', verbose_name='Perfil customizado'),
        ),
    ]
