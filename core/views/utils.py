"""
Utility functions shared across all views.
Includes: checkout validation, shipping calculation, payment utilities.
"""
import hashlib
import time
from decimal import Decimal
from django.core.cache import cache
from django.db.models import F
from ..models import Product


def generate_idempotency_key(cart_id, user_identifier):
    """Generate a unique idempotency key to prevent duplicate order submissions."""
    timestamp = int(time.time() // 300)  # 5-minute window
    raw_key = f"{cart_id}:{user_identifier}:{timestamp}"
    return hashlib.sha256(raw_key.encode()).hexdigest()[:32]


def validate_cart_for_checkout(cart):
    """Comprehensive cart validation for checkout - returns (is_valid, errors)."""
    errors = []
    
    if cart.total_items == 0:
        errors.append('Your cart is empty.')
        return False, errors
    
    # Re-verify stock and prices
    for item in cart.items.select_related('product').all():
        product = item.product
        
        if not product.is_active:
            errors.append(f'{product.title} is no longer available.')
            continue
        
        if product.track_inventory and not product.allow_backorder:
            if product.stock_quantity < item.quantity:
                errors.append(f'{product.title}: only {product.stock_quantity} available (you have {item.quantity})')
    
    return len(errors) == 0, errors


def build_shipping_methods(cart):
    """Construct shipping method options with dynamic pricing."""
    subtotal = cart.subtotal
    standard_cost = Decimal('0.00') if subtotal >= cart.FREE_SHIPPING_THRESHOLD else cart.get_shipping_estimate()
    standard_cost = standard_cost.quantize(Decimal('0.01'))

    express_cost = Decimal('12.00').quantize(Decimal('0.01'))

    return [
        {
            'id': 'standard',
            'label': 'Standard Shipping',
            'description': f"Free over ${int(cart.FREE_SHIPPING_THRESHOLD):,} or tiered flat rates",
            'eta': '5–7 business days',
            'cost': standard_cost,
            'display_cost': 'Free' if standard_cost == Decimal('0.00') else f"${standard_cost:.2f}",
            'badge': 'Most popular' if standard_cost == Decimal('0.00') else '',
        },
        {
            'id': 'express',
            'label': 'Express Shipping',
            'description': 'Priority handling & dispatch',
            'eta': '2–3 business days',
            'cost': express_cost,
            'display_cost': f"${express_cost:.2f}",
            'badge': 'Fastest',
        },
    ]


def calculate_order_totals(cart, shipping_method_id, province, shipping_methods=None):
    """Calculate shipping, tax, and order total for the given selections."""
    province = (province or 'ON').upper()
    shipping_methods = shipping_methods or build_shipping_methods(cart)
    methods_map = {m['id']: m for m in shipping_methods}
    selected = methods_map.get(shipping_method_id, shipping_methods[0])

    shipping_cost = selected['cost'].quantize(Decimal('0.01'))
    tax_rate = cart.TAX_RATES.get(province, cart.TAX_RATES.get('ON', Decimal('0.13')))
    tax_amount = (cart.subtotal * tax_rate).quantize(Decimal('0.01'))
    total = (cart.subtotal + shipping_cost + tax_amount).quantize(Decimal('0.01'))

    return {
        'shipping_methods': shipping_methods,
        'selected_method': selected,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'tax_rate': tax_rate,
        'grand_total': total,
        'province': province,
    }
