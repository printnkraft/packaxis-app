#!/usr/bin/env python
"""Reset database - drop entire schema and recreate"""
import os
import sys

# Check if we should skip reset
if os.environ.get('SKIP_DB_RESET', '').lower() == 'true':
    print("⏭️ Skipping database reset (SKIP_DB_RESET=true)")
    sys.exit(0)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')

import django
django.setup()

from django.db import connection

def reset_database():
    print("🗑️ Checking database state...")
    
    try:
        with connection.cursor() as cursor:
            # Check if the problematic index exists
            cursor.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE indexname = 'core_product_slug_8cf0d080_like'
            """)
            if cursor.fetchone():
                print("⚠️ Found orphaned index, dropping schema...")
                cursor.execute("DROP SCHEMA public CASCADE;")
                cursor.execute("CREATE SCHEMA public;")
                cursor.execute("GRANT ALL ON SCHEMA public TO public;")
                print("✅ Schema dropped and recreated!")
            else:
                # Check if any tables exist
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'
                """)
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"⚠️ Found {count} existing tables, dropping schema...")
                    cursor.execute("DROP SCHEMA public CASCADE;")
                    cursor.execute("CREATE SCHEMA public;")
                    cursor.execute("GRANT ALL ON SCHEMA public TO public;")
                    print("✅ Schema dropped and recreated!")
                else:
                    print("✅ Database is clean, proceeding...")
    except Exception as e:
        print(f"⚠️ Error checking/resetting database: {e}")

if __name__ == '__main__':
    reset_database()
