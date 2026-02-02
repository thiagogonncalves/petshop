# Generated for appointment enhancements and business hours

from django.db import migrations, models
import django.db.models.deletion


def populate_start_end(apps, schema_editor):
    """Populate start_at, end_at from scheduled_date for existing appointments."""
    from datetime import timedelta
    Appointment = apps.get_model('scheduling', 'Appointment')
    for apt in Appointment.objects.all():
        if apt.scheduled_date:
            apt.start_at = apt.scheduled_date
            apt.end_at = apt.scheduled_date + timedelta(minutes=30)
            apt.save(update_fields=['start_at', 'end_at'])


def reverse_populate(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='start_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Início'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='end_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Término'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='created_via',
            field=models.CharField(
                choices=[('admin', 'Administrador/Atendente'), ('client_self', 'Cliente (autoagendamento)')],
                default='admin',
                max_length=15,
                verbose_name='Criado via'
            ),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='scheduled_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data e Hora Agendada'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(
                choices=[
                    ('scheduled', 'Agendado'),
                    ('confirmed', 'Confirmado'),
                    ('in_progress', 'Em Andamento'),
                    ('completed', 'Concluído'),
                    ('done', 'Concluído'),
                    ('cancelled', 'Cancelado'),
                    ('no_show', 'Não Compareceu'),
                ],
                default='scheduled',
                max_length=15,
                verbose_name='Status'
            ),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_appointments',
                to='users.user',
                verbose_name='Criado por'
            ),
        ),
        migrations.RunPython(populate_start_end, reverse_populate),
        migrations.AlterField(
            model_name='appointment',
            name='start_at',
            field=models.DateTimeField(verbose_name='Início'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='end_at',
            field=models.DateTimeField(verbose_name='Término'),
        ),
        migrations.CreateModel(
            name='BusinessHoursConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot_minutes', models.PositiveIntegerField(default=30, verbose_name='Intervalo do slot (min)')),
                ('timezone', models.CharField(default='America/Fortaleza', max_length=50, verbose_name='Fuso horário')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Config. Horário de Funcionamento',
                'verbose_name_plural': 'Config. Horários de Funcionamento',
            },
        ),
        migrations.CreateModel(
            name='BusinessClosure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Data')),
                ('reason', models.CharField(blank=True, max_length=200, verbose_name='Motivo')),
            ],
            options={
                'verbose_name': 'Fechamento',
                'verbose_name_plural': 'Fechamentos',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='BusinessHoursRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.PositiveSmallIntegerField(verbose_name='Dia (0=Seg...6=Dom)')),
                ('is_open', models.BooleanField(default=True, verbose_name='Aberto')),
                ('open_time', models.TimeField(blank=True, null=True, verbose_name='Abertura')),
                ('close_time', models.TimeField(blank=True, null=True, verbose_name='Fechamento')),
                ('break_start', models.TimeField(blank=True, null=True, verbose_name='Início pausa')),
                ('break_end', models.TimeField(blank=True, null=True, verbose_name='Fim pausa')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rules', to='scheduling.businesshoursconfig', verbose_name='Configuração')),
            ],
            options={
                'verbose_name': 'Regra de Horário',
                'verbose_name_plural': 'Regras de Horário',
                'ordering': ['weekday'],
                'unique_together': {('config', 'weekday')},
            },
        ),
    ]
