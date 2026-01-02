"""
Auto-migrate on startup management command
This runs migrations automatically when Django starts
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run migrations automatically'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Running migrations...'))
        call_command('migrate', '--noinput')
        self.stdout.write(self.style.SUCCESS('✅ Migrations complete!'))
