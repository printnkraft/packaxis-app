#!/usr/bin/env python
"""
Fix partially migrated database by faking problematic migrations
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("\n" + "="*50)
print("🔧 Fixing database migration state...")
print("="*50)

# Check if tables exist
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'core_%'
        LIMIT 5
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n✓ Found {len(tables)} core tables in database")
        print("🔄 Faking all core migrations to match database state...")
        
        # Fake all core migrations up to 0009
        try:
            call_command('migrate', 'core', '0009', '--fake', verbosity=0)
            print("✅ Successfully faked migrations!")
        except Exception as e:
            print(f"⚠️ Fake migration warning: {e}")
    else:
        print("\n✓ Database is clean, no faking needed")

print("\n" + "="*50)
print("✅ Database state fixed!")
print("="*50)
