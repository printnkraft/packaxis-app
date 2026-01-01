#!/usr/bin/env python
"""
Migrate data from local SQLite to Railway Postgres
Run: python migrate_data.py
"""
import os
import sys
import django
import json
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.management import call_command
from io import StringIO

def export_local_data():
    """Export all data from local database to JSON"""
    print("📦 Exporting local data...")
    out = StringIO()
    call_command('dumpdata', '--all', '--indent', '2', stdout=out)
    data = out.getvalue()
    
    with open('local_data.json', 'w') as f:
        f.write(data)
    
    print(f"✅ Exported {len(data)} bytes to local_data.json")
    return data

if __name__ == '__main__':
    export_local_data()
    print("\n📋 Next steps:")
    print("1. Copy local_data.json to a safe place")
    print("2. On Railway, run: python manage.py loaddata local_data.json")
