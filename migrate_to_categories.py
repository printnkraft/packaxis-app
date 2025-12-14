"""
Script to migrate existing products to product categories and create default categories
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import Product, ProductCategory

def migrate_products_to_categories():
    """Copy all existing products to product categories"""
    products = Product.objects.all()
    migrated_count = 0
    
    for product in products:
        # Create or update product category
        category, created = ProductCategory.objects.update_or_create(
            title=product.title,
            defaults={
                'description': product.description,
                'image': product.image,
                'slug': product.slug,
                'order': product.order,
                'is_active': product.is_active,
                'material': product.material,
                'gsm_range': product.gsm_range,
                'handle_type': product.handle_type,
                'customization': product.customization,
                'feature_1': product.feature_1,
                'feature_2': product.feature_2,
                'feature_3': product.feature_3,
                'feature_4': product.feature_4,
                'feature_5': product.feature_5,
                'feature_6': product.feature_6,
            }
        )
        
        if created:
            print(f"✓ Created product category: {category.title}")
        else:
            print(f"✓ Updated product category: {category.title}")
        migrated_count += 1
    
    print(f"\n✓ Migrated {migrated_count} product(s) to product categories")

def create_default_categories():
    """Create the 5 default product categories mentioned by user"""
    categories_data = [
        {
            'title': 'Brown Kraft Bags',
            'description': 'Grocery & Food Packaging',
            'slug': 'brown-kraft-bags',
            'order': 1,
        },
        {
            'title': 'Shopping Paper Bags',
            'description': 'Retail Packaging',
            'slug': 'shopping-paper-bags',
            'order': 2,
        },
        {
            'title': 'Custom Branded Bags',
            'description': 'Luxury Custom Packaging',
            'slug': 'custom-branded-bags',
            'order': 3,
        },
        {
            'title': 'White Paper Bags',
            'description': 'Premium Retail Packaging',
            'slug': 'white-paper-bags',
            'order': 4,
        },
        {
            'title': 'Paper Straws',
            'description': 'Eco-Friendly Drinking Straws',
            'slug': 'paper-straws',
            'order': 5,
        },
    ]
    
    created_count = 0
    for category_data in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            slug=category_data['slug'],
            defaults=category_data
        )
        
        if created:
            print(f"✓ Created category: {category.title}")
            created_count += 1
        else:
            # Update existing
            for key, value in category_data.items():
                setattr(category, key, value)
            category.save()
            print(f"✓ Updated category: {category.title}")
    
    print(f"\n✓ Created/updated {len(categories_data)} default product categories")

if __name__ == '__main__':
    print("=== Migrating Products to Product Categories ===\n")
    
    # First migrate existing products
    migrate_products_to_categories()
    
    print("\n=== Creating Default Product Categories ===\n")
    # Then create/update default categories
    create_default_categories()
    
    print("\n✅ Migration complete!")
    print("\nNote: Old Product model is kept for backward compatibility but marked as deprecated.")
    print("Please use Product Categories from now on.")
