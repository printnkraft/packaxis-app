"""
Seed example tags and nested categories for demonstration
Run: python manage.py shell < seed_classification_examples.py
Or: python seed_classification_examples.py
"""

import os
import django

# Setup Django (if running as standalone script)
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
    django.setup()

from core.models import Tag, ProductCategory, Industry, Product
from django.utils.text import slugify

def create_tags():
    """Create example product tags"""
    tags_data = [
        {'name': 'Eco-Friendly', 'color': '#22C55E', 'description': 'Environmentally sustainable products', 'order': 1},
        {'name': 'Bulk Discount', 'color': '#3B82F6', 'description': 'Special pricing for bulk orders', 'order': 2},
        {'name': 'Custom Printing', 'color': '#8B5CF6', 'description': 'Supports custom logo/design printing', 'order': 3},
        {'name': 'Food Safe', 'color': '#F59E0B', 'description': 'Safe for direct food contact', 'order': 4},
        {'name': 'Bestseller', 'color': '#EF4444', 'description': 'Top selling product', 'order': 5},
        {'name': 'New Arrival', 'color': '#06B6D4', 'description': 'Recently added to catalog', 'order': 6},
        {'name': 'Made in USA', 'color': '#DC2626', 'description': 'Manufactured in the United States', 'order': 7},
        {'name': 'Recyclable', 'color': '#10B981', 'description': '100% recyclable materials', 'order': 8},
        {'name': 'Premium Quality', 'color': '#7C3AED', 'description': 'High-end quality materials', 'order': 9},
        {'name': 'Fast Shipping', 'color': '#F97316', 'description': 'Ships within 24 hours', 'order': 10},
    ]
    
    created_count = 0
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_data['name'],
            defaults={
                'slug': slugify(tag_data['name']),
                'color': tag_data['color'],
                'description': tag_data['description'],
                'order': tag_data['order'],
                'is_active': True
            }
        )
        if created:
            created_count += 1
            print(f"✅ Created tag: {tag.name} ({tag.color})")
        else:
            print(f"⏭️  Tag already exists: {tag.name}")
    
    print(f"\n🎉 Created {created_count} new tags (Total: {Tag.objects.count()})")


def create_nested_categories_example():
    """Create example nested category structure"""
    print("\n📂 Creating nested category structure...")
    
    # Create root category
    paper_packaging, _ = ProductCategory.objects.get_or_create(
        slug='paper-packaging',
        parent=None,
        defaults={
            'title': 'Paper Packaging',
            'description': 'All paper-based packaging solutions',
            'order': 1,
            'is_active': True
        }
    )
    print(f"✅ Root: {paper_packaging.title}")
    
    # Create level 1 subcategories
    bags, _ = ProductCategory.objects.get_or_create(
        slug='bags',
        parent=paper_packaging,
        defaults={
            'title': 'Bags',
            'description': 'Paper bags for various uses',
            'order': 1,
            'is_active': True
        }
    )
    print(f"  ✅ Level 1: {bags.get_full_path()}")
    
    boxes, _ = ProductCategory.objects.get_or_create(
        slug='boxes',
        parent=paper_packaging,
        defaults={
            'title': 'Boxes',
            'description': 'Paper boxes and containers',
            'order': 2,
            'is_active': True
        }
    )
    print(f"  ✅ Level 1: {boxes.get_full_path()}")
    
    # Create level 2 subcategories under Bags
    shopping_bags, _ = ProductCategory.objects.get_or_create(
        slug='shopping',
        parent=bags,
        defaults={
            'title': 'Shopping Bags',
            'description': 'Retail and shopping paper bags',
            'order': 1,
            'is_active': True
        }
    )
    print(f"    ✅ Level 2: {shopping_bags.get_full_path()}")
    
    gift_bags, _ = ProductCategory.objects.get_or_create(
        slug='gift',
        parent=bags,
        defaults={
            'title': 'Gift Bags',
            'description': 'Decorative gift bags',
            'order': 2,
            'is_active': True
        }
    )
    print(f"    ✅ Level 2: {gift_bags.get_full_path()}")
    
    # Create level 3 subcategories under Shopping Bags
    kraft_shopping, _ = ProductCategory.objects.get_or_create(
        slug='brown-kraft',
        parent=shopping_bags,
        defaults={
            'title': 'Brown Kraft',
            'description': 'Natural brown kraft shopping bags',
            'order': 1,
            'is_active': True
        }
    )
    print(f"      ✅ Level 3: {kraft_shopping.get_full_path()}")
    
    white_shopping, _ = ProductCategory.objects.get_or_create(
        slug='white-paper',
        parent=shopping_bags,
        defaults={
            'title': 'White Paper',
            'description': 'Premium white paper shopping bags',
            'order': 2,
            'is_active': True
        }
    )
    print(f"      ✅ Level 3: {white_shopping.get_full_path()}")


def create_nested_industries_example():
    """Create example nested industry structure"""
    print("\n🏢 Creating nested industry structure...")
    
    # Create root industries
    food_service, _ = Industry.objects.get_or_create(
        title='Food Service',
        defaults={
            'url': '/food-service/',
            'order': 1,
            'is_active': True
        }
    )
    print(f"✅ Root: {food_service.title}")
    
    # Level 1: Restaurant types under Food Service
    restaurants, _ = Industry.objects.get_or_create(
        title='Restaurants',
        parent=food_service,
        defaults={
            'url': '/food-service/restaurants/',
            'order': 1,
            'is_active': True
        }
    )
    print(f"  ✅ Level 1: {restaurants.get_full_path()}")
    
    catering, _ = Industry.objects.get_or_create(
        title='Catering Services',
        parent=food_service,
        defaults={
            'url': '/food-service/catering/',
            'order': 2,
            'is_active': True
        }
    )
    print(f"  ✅ Level 1: {catering.get_full_path()}")
    
    # Level 2: Restaurant subtypes
    fast_food, _ = Industry.objects.get_or_create(
        title='Fast Food',
        parent=restaurants,
        defaults={
            'url': '/food-service/restaurants/fast-food/',
            'order': 1,
            'is_active': True
        }
    )
    print(f"    ✅ Level 2: {fast_food.get_full_path()}")
    
    fine_dining, _ = Industry.objects.get_or_create(
        title='Fine Dining',
        parent=restaurants,
        defaults={
            'url': '/food-service/restaurants/fine-dining/',
            'order': 2,
            'is_active': True
        }
    )
    print(f"    ✅ Level 2: {fine_dining.get_full_path()}")
    
    cafes, _ = Industry.objects.get_or_create(
        title='Cafes & Coffee Shops',
        parent=restaurants,
        defaults={
            'url': '/food-service/restaurants/cafes/',
            'order': 3,
            'is_active': True
        }
    )
    print(f"    ✅ Level 2: {cafes.get_full_path()}")
    
    # Create another root industry: Retail
    retail, _ = Industry.objects.get_or_create(
        title='Retail',
        defaults={
            'url': '/retail/',
            'order': 2,
            'is_active': True
        }
    )
    print(f"\n✅ Root: {retail.title}")
    
    fashion, _ = Industry.objects.get_or_create(
        title='Fashion & Apparel',
        parent=retail,
        defaults={
            'url': '/retail/fashion/',
            'order': 1,
            'is_active': True
        }
    )
    print(f"  ✅ Level 1: {fashion.get_full_path()}")
    
    grocery, _ = Industry.objects.get_or_create(
        title='Grocery & Convenience',
        parent=retail,
        defaults={
            'url': '/retail/grocery/',
            'order': 2,
            'is_active': True
        }
    )
    print(f"  ✅ Level 1: {grocery.get_full_path()}")


def apply_tags_to_products():
    """Apply example tags to existing products"""
    print("\n🏷️  Applying tags to products...")
    
    # Get tags
    eco = Tag.objects.filter(name='Eco-Friendly').first()
    bulk = Tag.objects.filter(name='Bulk Discount').first()
    custom = Tag.objects.filter(name='Custom Printing').first()
    food_safe = Tag.objects.filter(name='Food Safe').first()
    bestseller = Tag.objects.filter(name='Bestseller').first()
    recyclable = Tag.objects.filter(name='Recyclable').first()
    
    # Apply tags to products
    products = Product.objects.filter(is_active=True)
    
    for product in products:
        tags_to_add = []
        
        # Add Eco-Friendly and Recyclable to kraft products
        if 'kraft' in product.title.lower() or 'brown' in product.title.lower():
            if eco:
                tags_to_add.append(eco)
            if recyclable:
                tags_to_add.append(recyclable)
        
        # Add Food Safe to grocery bags
        if 'grocery' in product.title.lower() or 'food' in product.title.lower():
            if food_safe:
                tags_to_add.append(food_safe)
        
        # Add Custom Printing to branded products
        if 'custom' in product.title.lower() or 'branded' in product.title.lower():
            if custom:
                tags_to_add.append(custom)
        
        # Add Bulk Discount to shopping bags
        if 'shopping' in product.title.lower():
            if bulk:
                tags_to_add.append(bulk)
        
        # Add Bestseller to first product
        if product.id == 1 and bestseller:
            tags_to_add.append(bestseller)
        
        if tags_to_add:
            product.tags.add(*tags_to_add)
            tag_names = ', '.join([t.name for t in tags_to_add])
            print(f"  ✅ {product.title}: {tag_names}")


def main():
    """Run all seeding functions"""
    print("🌱 Seeding Classification Examples...\n")
    print("=" * 60)
    
    try:
        create_tags()
        create_nested_categories_example()
        create_nested_industries_example()
        apply_tags_to_products()
        
        print("\n" + "=" * 60)
        print("✅ Seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   Tags: {Tag.objects.count()}")
        print(f"   Categories: {ProductCategory.objects.count()}")
        print(f"   Industries: {Industry.objects.count()}")
        print(f"   Products: {Product.objects.count()}")
        
        print("\n🔗 Next Steps:")
        print("   1. Visit: http://127.0.0.1:8000/superusers/core/tag/")
        print("   2. Visit: http://127.0.0.1:8000/superusers/core/productcategory/")
        print("   3. Visit: http://127.0.0.1:8000/superusers/core/industry/")
        print("   4. Edit products to add/remove tags")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
