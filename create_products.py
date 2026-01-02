#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import ProductCategory, Product
from django.utils.text import slugify

# Get or create categories
categories = ProductCategory.objects.all()
print(f"Found {categories.count()} categories")

# Create sample products for each category
products_data = [
    {
        'category_slug': 'shopping-paper-bags',
        'title': 'Standard Shopping Paper Bags',
        'description': 'Quality shopping bags for retail stores',
    },
    {
        'category_slug': 'brown-kraft-bags',
        'title': 'Brown Kraft Grocery Bags',
        'description': 'Eco-friendly kraft paper bags',
    },
    {
        'category_slug': 'white-paper-bags',
        'title': 'White Paper Bags',
        'description': 'Premium white paper bags',
    },
    {
        'category_slug': 'custom-branded-bags',
        'title': 'Custom Branded Paper Bags',
        'description': 'Personalized bags with your branding',
    },
    {
        'category_slug': 'paper-straws',
        'title': 'Eco-Friendly Paper Straws',
        'description': 'Sustainable drinking straws',
    },
]

for prod in products_data:
    cat = ProductCategory.objects.filter(slug=prod['category_slug']).first()
    if cat:
        product, created = Product.objects.get_or_create(
            slug=slugify(prod['title']),
            defaults={
                'title': prod['title'],
                'description': prod['description'],
                'category': cat,
                'is_active': True,
                'order': 1,
            }
        )
        status = 'Created' if created else 'Already exists'
        print(f'{status}: {product.title}')
    else:
        print(f'Category not found: {prod["category_slug"]}')

print('\nProducts loaded successfully!')
