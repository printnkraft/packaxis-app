"""
Shopping cart views.
Includes: cart display, add/update/remove, cart dropdown, quantity management.
"""
import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from ..models import Cart, CartItem, Product
from ..security import ratelimit_cart_api

logger = logging.getLogger(__name__)


def get_or_create_cart(request):
    """Get or create a cart for the current session"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    """Display shopping cart with tiered pricing"""
    cart = get_or_create_cart(request)
    
    # Prefetch products and their tiered prices for better performance
    cart_items = cart.items.select_related('product').prefetch_related('product__tiered_prices').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'core/cart.html', context)


@ratelimit_cart_api
def add_to_cart(request, slug):
    """Add a product to cart with rate limiting and validation"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = get_or_create_cart(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Parse and validate quantity
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        if quantity > 9999:
            quantity = 9999
    except (ValueError, TypeError):
        quantity = 1
    
    # Check if product price is set
    if not product.price or product.price <= 0:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'This product is not available for purchase.'
            })
        messages.error(request, 'This product is not available for purchase.')
        return redirect('core:product_detail', category_slug=product.category.slug if product.category else 'products', product_slug=slug)
    
    # Check stock if tracking inventory
    if product.track_inventory and not product.allow_backorder:
        if product.stock_quantity < quantity:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Sorry, only {product.stock_quantity} items available in stock.'
                })
            messages.error(request, f'Sorry, only {product.stock_quantity} items available in stock.')
            return redirect('core:product_detail', category_slug=product.category.slug if product.category else 'products', product_slug=slug)
    
    # Check minimum order quantity
    min_order_warning = None
    if product.minimum_order and quantity < product.minimum_order:
        min_order_warning = f'Minimum order quantity is {product.minimum_order} items. Quantity adjusted.'
        if not is_ajax:
            messages.warning(request, min_order_warning)
        quantity = product.minimum_order
    
    # Add to cart or update quantity (with race condition handling)
    try:
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Verify combined quantity doesn't exceed stock
            new_quantity = cart_item.quantity + quantity
            if product.track_inventory and not product.allow_backorder:
                if product.stock_quantity < new_quantity:
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': f'Cannot add more. You already have {cart_item.quantity} in cart and only {product.stock_quantity} available.'
                        })
                    messages.error(request, f'Cannot add more. You already have {cart_item.quantity} in cart.')
                    return redirect('core:cart')
            
            cart_item.quantity = new_quantity
            cart_item.save()
            if not is_ajax:
                messages.success(request, f'Updated quantity of "{product.title}" in your cart.')
        else:
            if not is_ajax:
                messages.success(request, f'Added "{product.title}" to your cart.')
    except Exception as e:
        logger.error(f'Error adding to cart: {str(e)}')
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Could not add item to cart. Please try again.'
            })
        messages.error(request, 'Could not add item to cart. Please try again.')
        return redirect('core:cart')
    
    # Return JSON for AJAX requests
    if is_ajax:
        response_data = {
            'success': True,
            'message': f'Added {quantity}x {product.title} to cart',
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'cart_count': cart.total_items,
        }
        if min_order_warning:
            response_data['warning'] = min_order_warning
        return JsonResponse(response_data)
    
    return redirect('core:cart')


@require_POST
def update_cart(request):
    """Update cart item quantity with tiered pricing support"""
    cart = get_or_create_cart(request)
    
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity <= 0:
            cart_item.delete()
            message = f'Removed "{cart_item.product.title}" from cart.'
            
            return JsonResponse({
                'success': True,
                'removed': True,
                'message': message,
                'cart_total_items': cart.total_items,
                'cart_subtotal': str(cart.subtotal),
                'original_subtotal': str(cart.original_subtotal),
                'total_savings': str(cart.total_savings),
            })
        else:
            # Check stock
            if cart_item.product.track_inventory and not cart_item.product.allow_backorder:
                if cart_item.product.stock_quantity < quantity:
                    return JsonResponse({
                        'success': False,
                        'message': f'Only {cart_item.product.stock_quantity} items available in stock.'
                    })
            
            cart_item.quantity = quantity
            cart_item.save()
            message = f'Updated quantity to {quantity}.'
            
            # Get tiered pricing info
            applied_tier = cart_item.applied_tier
            tier_label = applied_tier.label if applied_tier else None
            
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_total_items': cart.total_items,
                'cart_subtotal': str(cart.subtotal),
                'original_subtotal': str(cart.original_subtotal),
                'total_savings': str(cart.total_savings),
                'item_total': str(cart_item.total_price),
                'item_savings': str(cart_item.total_savings),
                'unit_price': str(cart_item.unit_price),
                'base_price': str(cart_item.base_price),
                'savings_percentage': cart_item.savings_percentage,
                'tier_label': tier_label or 'Volume Price' if cart_item.savings_percentage > 0 else None,
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def remove_from_cart(request, item_id):
    """Remove an item from cart"""
    cart = get_or_create_cart(request)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_title = cart_item.product.title
    cart_item.delete()
    
    messages.success(request, f'Removed "{product_title}" from your cart.')
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Removed from cart',
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
    
    return redirect('core:cart')


@require_POST
def update_cart_ajax(request, item_id):
    """AJAX endpoint for updating cart item quantity from dropdown"""
    cart = get_or_create_cart(request)
    
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        change = int(data.get('change', 0))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        new_quantity = cart_item.quantity + change
        
        if new_quantity <= 0:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'removed': True,
                'cart_total_items': cart.total_items,
                'cart_subtotal': str(cart.subtotal),
            })
        
        # Check stock
        if cart_item.product.track_inventory and not cart_item.product.allow_backorder:
            if cart_item.product.stock_quantity < new_quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {cart_item.product.stock_quantity} items available in stock.'
                })
        
        cart_item.quantity = new_quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'item_total': str(cart_item.total_price),
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
def remove_cart_ajax(request, item_id):
    """AJAX endpoint for removing cart item from dropdown"""
    cart = get_or_create_cart(request)
    
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
def set_cart_quantity_ajax(request, item_id):
    """AJAX endpoint for setting cart item quantity directly (manual input)"""
    cart = get_or_create_cart(request)
    
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Quantity must be at least 1.'
            })
        
        if quantity > 9999:
            return JsonResponse({
                'success': False,
                'error': 'Maximum quantity is 9999.'
            })
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # Check stock
        if cart_item.product.track_inventory and not cart_item.product.allow_backorder:
            if cart_item.product.stock_quantity < quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {cart_item.product.stock_quantity} items available in stock.'
                })
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'new_quantity': quantity,
            'item_total': str(cart_item.total_price),
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid quantity value.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def cart_dropdown_html(request):
    """Returns the cart dropdown HTML for AJAX updates"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart_items_preview': cart_items[:3],
        'cart_total_items': cart.total_items,
        'cart_subtotal': cart.subtotal,
    }
    
    return render(request, 'core/partials/cart_dropdown_content.html', context)
