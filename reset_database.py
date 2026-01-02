#!/usr/bin/env python
"""
Reset the PostgreSQL database completely and run fresh migrations
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

print("\n" + "="*50)
print("🔥 Resetting Database Completely...")
print("="*50)

# Drop all tables and constraints
with connection.cursor() as cursor:
    print("\n🗑️  Dropping all existing tables...")
    
    # Get all tables
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"   Found {len(tables)} tables to drop")
        
        # Drop all tables
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                print(f"   ✓ Dropped {table_name}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {table_name}: {e}")
        
        connection.commit()
        print("✅ All tables dropped!")
    else:
        print("✓ Database already empty")

print("\n" + "="*50)
print("✅ Database reset complete!")
print("="*50)
