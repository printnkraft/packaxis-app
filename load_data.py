#!/usr/bin/env python
"""Load data backup into the database"""
import os
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')

import django
django.setup()

from django.core import serializers
from django.db import transaction

def load_data():
    print("📦 Loading data from data_backup.json...")
    
    with open('data_backup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert back to Django format
    objects_to_save = []
    
    for item in data:
        try:
            # Recreate the serialized format Django expects
            obj_data = json.dumps([item])
            for obj in serializers.deserialize('json', obj_data):
                objects_to_save.append(obj)
        except Exception as e:
            print(f"⚠ Skipped: {item.get('model', 'unknown')} - {e}")
    
    # Save all objects
    with transaction.atomic():
        for obj in objects_to_save:
            try:
                obj.save()
            except Exception as e:
                print(f"⚠ Error saving {obj.object}: {e}")
    
    print(f"✅ Loaded {len(objects_to_save)} objects into database")

if __name__ == '__main__':
    load_data()
