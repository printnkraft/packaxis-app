#!/usr/bin/env python
"""Export database data with proper UTF-8 encoding in Django loaddata format"""
import os
import sys
import json
import io

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')

import django
django.setup()

from django.core.management import call_command

def export_data():
    print("📦 Exporting data in Django fixture format...")
    
    # Use StringIO with UTF-8 to capture output
    output = io.StringIO()
    
    try:
        call_command(
            'dumpdata',
            '--exclude', 'auth.permission',
            '--exclude', 'contenttypes',
            '--exclude', 'admin.logentry', 
            '--exclude', 'sessions',
            '--exclude', 'axes',
            '--indent', '2',
            stdout=output
        )
        
        data = output.getvalue()
        
        # Write to file with UTF-8 encoding
        with open('data_backup.json', 'w', encoding='utf-8') as f:
            f.write(data)
        
        print(f"✅ Exported data to data_backup.json ({len(data)} bytes)")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
        # Fallback: export specific apps only
        print("📦 Trying fallback export (core, blog, accounts apps only)...")
        
        output2 = io.StringIO()
        call_command(
            'dumpdata',
            'core', 'blog', 'accounts', 'sites', 'auth.user',
            '--indent', '2',
            stdout=output2
        )
        
        data = output2.getvalue()
        with open('data_backup.json', 'w', encoding='utf-8') as f:
            f.write(data)
        
        print(f"✅ Exported core data to data_backup.json ({len(data)} bytes)")

if __name__ == '__main__':
    export_data()

