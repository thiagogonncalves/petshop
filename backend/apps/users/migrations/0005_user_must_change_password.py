# Generated migration - add must_change_password and create default admin

from django.db import migrations, models


def create_default_admin(apps, schema_editor):
    User = apps.get_model('users', 'User')
    if not User.objects.exists():
        User.objects.create_user(
            username='admin',
            email='admin@localhost',
            password='admin',
            first_name='Administrador',
            last_name='',
            role='admin',
            must_change_password=True,
            is_staff=True,
            is_superuser=True,
        )


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_companysettings_theme'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='must_change_password',
            field=models.BooleanField(default=False, verbose_name='Alterar senha no próximo login'),
        ),
        migrations.RunPython(create_default_admin, reverse_noop),
    ]
