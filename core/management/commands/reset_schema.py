from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drops and recreates the public schema to fix orphaned indexes'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            try:
                self.stdout.write("Checking for orphaned indexes...")
                cursor.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE indexname = 'core_product_slug_8cf0d080_like'
                """)
                result = cursor.fetchone()
                
                if result:
                    self.stdout.write(self.style.WARNING("Found orphaned index, dropping schema..."))
                    cursor.execute("DROP SCHEMA public CASCADE;")
                    cursor.execute("CREATE SCHEMA public;")
                    cursor.execute("GRANT ALL ON SCHEMA public TO public;")
                    cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
                    self.stdout.write(self.style.SUCCESS("Schema recreated successfully"))
                else:
                    self.stdout.write(self.style.SUCCESS("No orphaned indexes found, schema is clean"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
