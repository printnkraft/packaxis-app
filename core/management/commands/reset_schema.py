from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Drops and recreates the public schema to fix orphaned indexes'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            try:
                self.stdout.write("Dropping and recreating schema...")
                cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
                cursor.execute("CREATE SCHEMA public;")
                cursor.execute("GRANT ALL ON SCHEMA public TO public;")
                cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
                self.stdout.write(self.style.SUCCESS("Schema recreated successfully"))
                
                # Create all tables from models
                self.stdout.write("Creating tables from models...")
                call_command('migrate', '--run-syncdb', verbosity=0)
                self.stdout.write(self.style.SUCCESS("Tables created successfully"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
