"""
Auto-create Django superuser from environment variables
Run this with: python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@packaxis.ca')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not password:
    print("❌ DJANGO_SUPERUSER_PASSWORD environment variable not set!")
    exit(1)

if User.objects.filter(username=username).exists():
    print(f"✅ Superuser '{username}' already exists")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser '{username}' created successfully!")
