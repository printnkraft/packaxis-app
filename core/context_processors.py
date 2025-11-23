from .models import MenuItem, Product

def menu_items(request):
    """Make menu items available to all templates"""
    top_level_items = MenuItem.objects.filter(is_active=True, parent=None)
    return {
        'menu_items': top_level_items
    }

def active_products(request):
    """Make active products available to all templates"""
    products = Product.objects.filter(is_active=True)
    return {
        'products': products,
        'active_products_count': products.count()
    }
