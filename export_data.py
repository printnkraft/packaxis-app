#!/usr/bin/env python
"""Export database data with proper UTF-8 encoding"""
import os
import sys
import json

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')

import django
django.setup()

from django.core import serializers
from django.apps import apps

def export_data():
    # Get all models
    exclude_models = ['auth.permission', 'contenttypes.contenttype']
    
    all_objects = []
    
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            model_label = f"{model._meta.app_label}.{model._meta.model_name}"
            if model_label.lower() not in [e.lower() for e in exclude_models]:
                try:
                    objects = model.objects.all()
                    if objects.exists():
                        data = serializers.serialize('python', objects)
                        all_objects.extend(data)
                        print(f"✓ Exported {model_label}: {objects.count()} objects")
                except Exception as e:
                    print(f"✗ Skipped {model_label}: {e}")
    
    # Write to file with UTF-8 encoding
    with open('data_backup.json', 'w', encoding='utf-8') as f:
        json.dump(all_objects, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Exported {len(all_objects)} total objects to data_backup.json")

if __name__ == '__main__':
    export_data()
