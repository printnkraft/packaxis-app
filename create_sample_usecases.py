import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import UseCase
from datetime import datetime

# Create sample use cases
use_cases_data = [
    {'title': 'Restaurants & Cafes', 'description': 'Perfect for takeout orders, delivery bags, and branded customer packaging.', 'icon_name': 'coffee', 'order': 1},
    {'title': 'Retail Stores', 'description': 'Enhance customer experience with premium branded shopping bags.', 'icon_name': 'shopping-bag', 'order': 2},
    {'title': 'E-commerce', 'description': 'Sustainable shipping and product packaging for online orders.', 'icon_name': 'box', 'order': 3},
    {'title': 'Corporate Gifts', 'description': 'Elegant presentation bags for events, promotions, and client gifts.', 'icon_name': 'gift', 'order': 4},
    {'title': 'Bakeries & Pastry Shops', 'description': 'Food-safe bags perfect for baked goods and pastries.', 'icon_name': 'coffee', 'order': 5},
    {'title': 'Boutiques & Fashion', 'description': 'Premium packaging to match your brand identity.', 'icon_name': 'shopping-bag', 'order': 6},
    {'title': 'Grocery Stores', 'description': 'Durable bags for groceries and everyday shopping needs.', 'icon_name': 'shopping-bag', 'order': 7},
    {'title': 'Event & Trade Shows', 'description': 'Branded bags for conferences, exhibitions, and promotional events.', 'icon_name': 'users', 'order': 8},
    {'title': 'Hotels & Hospitality', 'description': 'Welcome bags, amenity packaging, and guest room supplies.', 'icon_name': 'home', 'order': 9},
    {'title': 'Delivery Services', 'description': 'Reliable packaging for courier and delivery businesses.', 'icon_name': 'truck', 'order': 10},
]

created_count = 0
for uc_data in use_cases_data:
    use_case, created = UseCase.objects.get_or_create(
        title=uc_data['title'],
        defaults={
            'description': uc_data['description'],
            'icon_name': uc_data['icon_name'],
            'order': uc_data['order'],
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }
    )
    if created:
        created_count += 1
        print(f"✓ Created: {use_case.title}")
    else:
        print(f"  Already exists: {use_case.title}")

print(f"\n✓ Total use cases created: {created_count}/{len(use_cases_data)}")
print(f"✓ Total use cases in database: {UseCase.objects.count()}")
