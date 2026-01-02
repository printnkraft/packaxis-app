from django.core.cache import cache
from django.conf import settings
from .models import MenuItem, Product, ProductCategory, Cart
from allauth.socialaccount.models import SocialApp


def google_oauth_enabled(request):
    """Check if Google OAuth is configured and available (with caching)"""
    # Check cache first (1 hour TTL)
    enabled = cache.get('google_oauth_enabled')
    
    if enabled is None:
        try:
            google_app = SocialApp.objects.get(provider='google')
            enabled = True
        except SocialApp.DoesNotExist:
            enabled = False
        
        # Cache the result for 1 hour
        cache.set('google_oauth_enabled', enabled, 3600)
    
    return {
        'google_oauth_enabled': enabled,
    }


def menu_items(request):
    """Make menu items available to all templates (with caching)"""
    # Check cache first (1 hour TTL)
    top_level_items = cache.get('top_level_menu_items')
    
    if top_level_items is None:
        top_level_items = MenuItem.objects.filter(is_active=True, parent=None)
        # Cache the result for 1 hour
        cache.set('top_level_menu_items', list(top_level_items), 3600)
    
    return {
        'menu_items': top_level_items
    }

def product_categories_context(request):
    """Make active product categories available to all templates (with caching)"""
    # Check cache first (1 hour TTL)
    product_categories = cache.get('active_product_categories')
    
    if product_categories is None:
        product_categories = ProductCategory.objects.filter(is_active=True)
        # Cache the result for 1 hour
        cache.set('active_product_categories', list(product_categories), 3600)
    
    # Keep 'products' for backward compatibility, but prefer 'product_categories'
    return {
        'product_categories': product_categories,  # Preferred variable name
        'products': product_categories,  # Deprecated - use product_categories instead
        'active_products_count': len(product_categories)
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
