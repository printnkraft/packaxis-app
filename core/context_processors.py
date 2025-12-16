from .models import MenuItem, Product, ProductCategory, Cart

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


def cart_context(request):
    """Make cart information available to all templates"""
    cart_total_items = 0
    cart_items = []
    cart_subtotal = 0
    
    if request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            cart_total_items = cart.total_items
            cart_items = cart.items.select_related('product')[:3]  # Limit to 3 items for dropdown
            cart_subtotal = cart.subtotal
        except Cart.DoesNotExist:
            pass
    
    return {
        'cart_total_items': cart_total_items,
        'cart_items_preview': cart_items,
        'cart_subtotal': cart_subtotal
    }
