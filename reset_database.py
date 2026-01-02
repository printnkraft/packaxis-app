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
    print("\n🗑️  Dropping all database objects...")
    
    # Drop all views first
    cursor.execute("""
        SELECT table_name FROM information_schema.views 
        WHERE table_schema = 'public'
    """)
    views = cursor.fetchall()
    for view in views:
        cursor.execute(f'DROP VIEW IF EXISTS "{view[0]}" CASCADE')
    
    # Drop all tables
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"   Found {len(tables)} tables")
        
        # Drop all tables with CASCADE to remove dependent objects
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                print(f"   ✓ Dropped table {table_name}")
            except Exception as e:
                print(f"   ⚠️  Error with {table_name}: {e}")
    
    # Drop all sequences
    cursor.execute("""
        SELECT sequence_name FROM information_schema.sequences
        WHERE sequence_schema = 'public'
    """)
    sequences = cursor.fetchall()
    for seq in sequences:
        cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq[0]}" CASCADE')
        print(f"   ✓ Dropped sequence {seq[0]}")
    
    # Drop all custom types
    cursor.execute("""
        SELECT typname FROM pg_type 
        WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        AND typtype = 'e'
    """)
    types = cursor.fetchall()
    for typ in types:
        cursor.execute(f'DROP TYPE IF EXISTS "{typ[0]}" CASCADE')
        print(f"   ✓ Dropped type {typ[0]}")
    
    connection.commit()
    print("✅ All database objects dropped!")
    
print("\n" + "="*50)
print("✅ Database reset complete!")
print("="*50)
