import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import Industry

# Define industries with their URLs
industries_data = [
    {
        'title': 'Restaurant & Takeout',
        'url': '/restaurant-paper-bags/',
        'order': 1,
    },
    {
        'title': 'Retail Stores',
        'url': '/retail-paper-bags/',
        'order': 2,
    },
    {
        'title': 'Boutique & Fashion',
        'url': '/boutique-packaging/',
        'order': 3,
    },
    {
        'title': 'Grocery & Supermarket',
        'url': '/grocery-paper-bags/',
        'order': 4,
    },
    {
        'title': 'Bakery & Cafe',
        'url': '/bakery-paper-bags/',
        'order': 5,
    },
]

print("Creating industries...")
for data in industries_data:
    industry, created = Industry.objects.get_or_create(
        title=data['title'],
        defaults={
            'url': data['url'],
            'order': data['order'],
            'is_active': True,
        }
    )
    if created:
        print(f"✓ Created: {industry.title}")
    else:
        # Update existing
        industry.url = data['url']
        industry.order = data['order']
        industry.is_active = True
        industry.save()
        print(f"✓ Updated: {industry.title}")

print("\nNote: You still need to upload images for each industry in the Django admin.")
print("Go to http://127.0.0.1:8000/admin/core/industry/ to add images.")
