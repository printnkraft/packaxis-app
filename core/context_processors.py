from .models import MenuItem, Product, ProductCategory

def menu_items(request):
    """Make menu items available to all templates"""
    top_level_items = MenuItem.objects.filter(is_active=True, parent=None)
    return {
        'menu_items': top_level_items
    }

def active_products(request):
    """Make active product categories available to all templates"""
    product_categories = ProductCategory.objects.filter(is_active=True)
    # Keep 'products' for backward compatibility, but use product_categories
    return {
        'products': product_categories,  # Backward compatibility
        'product_categories': product_categories,
        'active_products_count': product_categories.count()
    }
