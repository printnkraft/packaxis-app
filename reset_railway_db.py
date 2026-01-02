#!/usr/bin/env python
"""
Reset Railway PostgreSQL database completely.
This drops all tables and lets Django migrations run fresh.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from django.db import connection

def reset_database():
    """Drop all tables, indexes, and reset to empty database"""
    print("=" * 60)
    print("🗑️  RESETTING DATABASE - All data will be lost!")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Drop all indexes first (they can be orphaned)
        print("\n🗂️  Dropping all indexes...")
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname NOT LIKE 'pg_%';
        """)
        indexes = cursor.fetchall()
        for index in indexes:
            try:
                cursor.execute(f'DROP INDEX IF EXISTS "{index[0]}" CASCADE;')
                print(f"   ✓ Dropped index {index[0]}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {index[0]}: {e}")
        
        # Get all table names
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public';
        """)
        tables = cursor.fetchall()
        
        if not tables and not indexes:
            print("✅ Database is already empty")
            return
        
        print(f"\n📋 Found {len(tables)} tables to drop:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Drop all tables with CASCADE
        print("\n🔥 Dropping all tables...")
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}" CASCADE;')
            print(f"   ✓ Dropped {table[0]}")
        
        # Drop django_migrations table to reset migration history
        cursor.execute('DROP TABLE IF EXISTS django_migrations CASCADE;')
        print("   ✓ Dropped django_migrations")
        
        print("\n✅ Database reset complete!")
        print("Next: Run migrations with `python manage.py migrate`")

if __name__ == '__main__':
    reset_database()
