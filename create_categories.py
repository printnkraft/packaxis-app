#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import ProductCategory
from django.utils.text import slugify

categories = [
    {'title': 'Shopping Paper Bags', 'description': 'High-quality shopping paper bags for retail and e-commerce', 'order': 1},
    {'title': 'Brown Kraft Bags', 'description': 'Eco-friendly brown kraft paper bags', 'order': 2},
    {'title': 'White Paper Bags', 'description': 'Clean white paper bags for premium packaging', 'order': 3},
    {'title': 'Custom Branded Bags', 'description': 'Customize your bags with your brand', 'order': 4},
    {'title': 'Paper Straws', 'description': 'Eco-friendly paper straws for beverages', 'order': 5},
]

for cat in categories:
    pc, created = ProductCategory.objects.get_or_create(
        slug=slugify(cat['title']),
        defaults={
            'title': cat['title'],
            'description': cat['description'],
            'order': cat['order'],
            'is_active': True,
        }
    )
    status = 'Created' if created else 'Already exists'
    print(f'{status}: {pc.title} (slug: {pc.slug})')

print('\nAll categories loaded successfully!')
