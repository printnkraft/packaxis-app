import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis_app.settings')
django.setup()

from core.models import Product

# Reorder products by popularity
# Most popular order: Shopping bags, Custom branded, Brown kraft, White paper, Paper straws

product_order = {
    'shopping-paper-bags': 1,      # Most popular - general purpose
    'custom-branded-bags': 2,       # High demand for branding
    'brown-kraft-bags': 3,          # Classic eco-friendly choice
    'white-paper-bags': 4,          # Premium option
    'paper-straws': 5,              # Complementary accessory
}

print("Reordering products by popularity...")
print("-" * 50)

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

print("-" * 50)
print("\nUpdated product order:")
products = Product.objects.all().order_by('order')
for p in products:
    badge = " [BESTSELLER]" if p.order == 1 else ""
    print(f"{p.order}. {p.title}{badge}")

print("\n✓ Products reordered successfully!")
