import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import Product

# Reorder to feature Brown Kraft Bags as the top product
# Brown Kraft Bags will be #1 (bestseller badge)

product_order = {
    'brown-kraft-bags': 1,          # Featured - eco-friendly focus
    'shopping-paper-bags': 2,       # General purpose
    'custom-branded-bags': 3,       # Branding option
    'white-paper-bags': 4,          # Premium option
    'paper-straws': 5,              # Complementary accessory
}

print("Reordering products to feature Brown Kraft Bags...")
print("-" * 60)

for slug, new_order in product_order.items():
    try:
        product = Product.objects.get(slug=slug)
        old_order = product.order
        product.order = new_order
        product.save()
        print(f"✓ {product.title}")
        print(f"  Order: {old_order} → {new_order}")
    except Product.DoesNotExist:
        print(f"✗ Product with slug '{slug}' not found")

print("-" * 60)
print("\nUpdated product order (Brown Kraft Bags is now featured):")
products = Product.objects.all().order_by('order')
for p in products:
    badge = " 🌟 [BESTSELLER - ECO-FRIENDLY FOCUS]" if p.order == 1 else ""
    print(f"{p.order}. {p.title}{badge}")

print("\n✓ Brown Kraft Bags is now your featured product!")
