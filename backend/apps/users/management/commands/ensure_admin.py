"""
Garante que o usuário admin exista com credenciais admin/admin.
Use quando não conseguir fazer login (ex.: usuário não foi criado ou senha alterada).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Garante usuário admin (admin/admin). Cria se não existir; com --reset redefine a senha.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Redefine a senha do admin para "admin" mesmo que o usuário já exista.',
        )

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin'

        user = User.objects.filter(username=username).first()
        if user:
            if options['reset']:
                user.set_password(password)
                user.is_active = True
                user.must_change_password = True
                user.save(update_fields=['password', 'is_active', 'must_change_password', 'updated_at'])
                self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" encontrado. Senha redefinida para "admin".'))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Usuário "{username}" já existe. Use --reset para redefinir a senha para "admin".'
                    )
                )
            return

        User.objects.create_user(
            username=username,
            email='admin@localhost',
            password=password,
            first_name='Administrador',
            last_name='',
            role='admin',
            must_change_password=True,
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado. Login: admin / admin'))
