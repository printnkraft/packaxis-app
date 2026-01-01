from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

class Command(BaseCommand):
    help = 'Drops schema and creates tables directly from models, skipping migrations'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            self.stdout.write("Dropping schema...")
            cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
            cursor.execute("GRANT USAGE ON SCHEMA public TO postgres;")
            self.stdout.write(self.style.SUCCESS("Schema recreated"))

        # Create tables from current models
        self.stdout.write("Creating tables from models...")
        with connection.schema_editor() as schema_editor:
            # Create all app tables
            for model in apps.get_models():
                try:
                    schema_editor.create_model(model)
                    self.stdout.write(f"  ✓ {model._meta.db_table}")
                except Exception as e:
                    # Table may already exist, that's fine
                    if "already exists" not in str(e):
                        self.stdout.write(self.style.WARNING(f"  ⚠ {model._meta.db_table}: {e}"))
        
        self.stdout.write(self.style.SUCCESS("Database ready"))

