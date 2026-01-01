#!/usr/bin/env python
"""Reset database - drop entire schema and recreate"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')

import django
django.setup()

from django.db import connection

def reset_database():
    print("🗑️ Resetting database - dropping entire schema...")
    
    try:
        with connection.cursor() as cursor:
            # Drop and recreate public schema - this removes EVERYTHING
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
            cursor.execute("GRANT ALL ON SCHEMA public TO public;")
            print("✅ Schema dropped and recreated successfully!")
    except Exception as e:
        print(f"⚠️ Schema reset error: {e}")
        # Fallback - try dropping individual objects
        print("Trying fallback method...")
        with connection.cursor() as cursor:
            cursor.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            print("✅ Tables dropped via fallback method!")
    
    print("✅ Database reset complete!")

if __name__ == '__main__':
    reset_database()
