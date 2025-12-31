#!/usr/bin/env python
"""Reset database - drop all tables and indexes before migration"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')

import django
django.setup()

from django.db import connection

def reset_database():
    print("🗑️ Resetting database...")
    
    with connection.cursor() as cursor:
        # Get all table names
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if tables:
            print(f"Found {len(tables)} tables to drop")
            # Disable foreign key checks and drop all tables
            cursor.execute("SET session_replication_role = 'replica';")
            for table in tables:
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                    print(f"  Dropped table: {table}")
                except Exception as e:
                    print(f"  Error dropping {table}: {e}")
            cursor.execute("SET session_replication_role = 'origin';")
        else:
            print("No tables found")
        
        # Also drop any orphaned indexes
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE schemaname = 'public'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        if indexes:
            print(f"Found {len(indexes)} indexes to drop")
            for index in indexes:
                try:
                    cursor.execute(f'DROP INDEX IF EXISTS "{index}" CASCADE')
                    print(f"  Dropped index: {index}")
                except Exception as e:
                    print(f"  Error dropping {index}: {e}")
        
        # Drop sequences
        cursor.execute("""
            SELECT sequence_name FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        """)
        sequences = [row[0] for row in cursor.fetchall()]
        
        if sequences:
            print(f"Found {len(sequences)} sequences to drop")
            for seq in sequences:
                try:
                    cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq}" CASCADE')
                    print(f"  Dropped sequence: {seq}")
                except Exception as e:
                    print(f"  Error dropping {seq}: {e}")
    
    print("✅ Database reset complete!")

if __name__ == '__main__':
    reset_database()
