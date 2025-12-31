#!/usr/bin/env python
"""Load data backup into the database"""
import os
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection

def check_data_exists():
    """Check if data already exists in the database"""
    from core.models import ProductCategory, MenuItem
    return ProductCategory.objects.exists() or MenuItem.objects.exists()

def load_data():
    print("📦 Checking if data needs to be loaded...")
    
    if check_data_exists():
        print("✅ Data already exists in database, skipping load")
        return
    
    if not os.path.exists('data_backup.json'):
        print("⚠ data_backup.json not found, skipping load")
        return
    
    print("📦 Loading data from data_backup.json...")
    
    try:
        # Use Django's loaddata command which handles dependencies correctly
        call_command('loaddata', 'data_backup.json', verbosity=2)
        print("✅ Data loaded successfully!")
    except Exception as e:
        print(f"⚠ Error loading data: {e}")
        # Try alternative approach - load without natural keys
        try:
            print("📦 Trying alternative load method...")
            call_command('loaddata', 'data_backup.json', '--ignorenonexistent', verbosity=2)
            print("✅ Data loaded with alternative method!")
        except Exception as e2:
            print(f"❌ Failed to load data: {e2}")

if __name__ == '__main__':
    load_data()

