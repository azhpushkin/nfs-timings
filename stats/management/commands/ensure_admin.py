from getpass import getpass

from django.core.management.base import BaseCommand, CommandError

from stats.models import User


class Command(BaseCommand):
    help = 'Creates or updates an active superuser without persisting its password.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument(
            '--password-stdin',
            action='store_true',
            help='Read the password from standard input instead of prompting.',
        )

    def handle(self, *args, username: str, password_stdin: bool, **options):
        password = input() if password_stdin else getpass('Admin password: ')
        password = password.rstrip('\r\n')
        if not password:
            raise CommandError('Admin password must not be empty.')

        user, created = User.objects.get_or_create(username=username)
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} admin user "{username}".'))
