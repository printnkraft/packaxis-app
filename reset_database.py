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

# Nuclear option: Drop and recreate the public schema
with connection.cursor() as cursor:
    print("\n🗑️  Dropping entire public schema...")
    
    try:
        # Drop the entire public schema (removes EVERYTHING)
        cursor.execute('DROP SCHEMA public CASCADE')
        print("   ✓ Public schema dropped")
        
        # Recreate the public schema
        cursor.execute('CREATE SCHEMA public')
        print("   ✓ Public schema recreated")
        
        # Grant permissions
        cursor.execute('GRANT ALL ON SCHEMA public TO PUBLIC')
        print("   ✓ Permissions granted")
        
        connection.commit()
        print("✅ Database completely wiped clean!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()
    
print("\n" + "="*50)
print("✅ Database reset complete!")
print("="*50)
