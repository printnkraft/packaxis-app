"""
AJAX API endpoints.
Includes: promo codes, product reviews, rate limiting errors.
"""
import json
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import PromoCode, Product, ProductReview, Order
from ..security import sanitize_text

logger = logging.getLogger(__name__)


@require_POST
def apply_promo_code(request):
    """Validate and apply a promo code to the cart session"""
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        email = data.get('email', '').strip()
        
        if not code:
            return JsonResponse({'success': False, 'error': 'Please enter a promo code.'})
        
        # Import here to avoid circular imports
        from .cart import get_or_create_cart
        
        # Get cart for subtotal
        cart = get_or_create_cart(request)
        if cart.total_items == 0:
            return JsonResponse({'success': False, 'error': 'Your cart is empty.'})
        
        # Find the promo code
        try:
            promo = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid promo code.'})
        
        # Validate the promo code
        is_valid, message = promo.is_valid(cart.subtotal, email)
        if not is_valid:
            return JsonResponse({'success': False, 'error': message})
        
        # Calculate discount
        shipping_cost = Decimal('0.00')  # Will be recalculated at checkout
        discount_amount = promo.calculate_discount(cart.subtotal, shipping_cost)
        
        # Store in session
        request.session['promo_code'] = code
        request.session['promo_discount'] = str(discount_amount)
        request.session.modified = True
        
        discount_label = ""
        if promo.discount_type == 'percentage':
            discount_label = f"{promo.discount_value}% off"
        elif promo.discount_type == 'fixed':
            discount_label = f"${promo.discount_value} off"
        elif promo.discount_type == 'free_shipping':
            discount_label = "Free shipping"
        
        return JsonResponse({
            'success': True,
            'code': code,
            'discount': float(discount_amount),
            'discount_label': discount_label,
            'message': f'Promo code "{code}" applied! {discount_label}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request.'})
    except Exception as e:
        logger.error(f'Error applying promo code: {str(e)}')
        return JsonResponse({'success': False, 'error': 'Something went wrong. Please try again.'})


@require_POST  
def remove_promo_code(request):
    """Remove promo code from session"""
    if 'promo_code' in request.session:
        del request.session['promo_code']
    if 'promo_discount' in request.session:
        del request.session['promo_discount']
    request.session.modified = True
    
    return JsonResponse({'success': True, 'message': 'Promo code removed.'})


@require_POST
@login_required(login_url='accounts:login')
def submit_review(request, category_slug, product_slug):
    """Submit a product review - only for customers who have purchased and received the product"""
    try:
        product = Product.objects.get(slug=product_slug, is_active=True)
        
        # Check if user has purchased and received this product
        delivered_order = Order.objects.filter(
            user=request.user,
            items__product=product,
            status='delivered'
        ).first()
        
        if not delivered_order:
            return JsonResponse({
                'error': 'You can only review products you have purchased and received.'
            }, status=403)
        
        # Check if user already reviewed this product (by email from order)
        existing_review = ProductReview.objects.filter(
            product=product,
            email=delivered_order.email
        ).first()
        
        if existing_review:
            return JsonResponse({
                'error': 'You have already reviewed this product.'
            }, status=400)
        
        # Get form data
        rating = int(request.POST.get('rating', 0))
        title = sanitize_text(request.POST.get('title', ''))
        review_text = sanitize_text(request.POST.get('review', ''))
        
        # Get user's name safely
        user_name = ''
        if hasattr(request.user, 'get_full_name'):
            user_name = request.user.get_full_name()
        if not user_name and hasattr(request.user, 'username'):
            user_name = request.user.username
        if not user_name:
            user_name = 'Anonymous'
            
        name = sanitize_text(request.POST.get('name', user_name))
        
        # Validate
        if not (1 <= rating <= 5):
            return JsonResponse({'error': 'Invalid rating. Please select 1-5 stars.'}, status=400)
        
        if not review_text or len(review_text) < 10:
            return JsonResponse({'error': 'Please write at least 10 characters for your review.'}, status=400)
        
        # Create review
        review = ProductReview.objects.create(
            product=product,
            order=delivered_order,
            email=delivered_order.email,
            name=name,
            rating=rating,
            title=title,
            review=review_text,
            is_verified=True,  # Verified because linked to order
            is_approved=True   # Auto-approve verified purchases
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your review! It will appear shortly.'
        })
        
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found.'}, status=404)
    except Exception as e:
        logger.error(f'Review submission error: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'error': f'Failed to submit review: {str(e)}'}, status=500)


def ratelimit_error(request, exception=None):
    """
    Custom view for rate limit exceeded errors.
    Used by django-ratelimit when a rate limit is exceeded.
    """
    logger.warning(f'Rate limit exceeded for IP: {request.META.get("REMOTE_ADDR")}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # For AJAX requests, return JSON
        return JsonResponse({
            'error': 'Too many requests. Please try again later.',
            'retry_after': 60  # seconds
        }, status=429)
    
    # For regular requests, render an error page
    return render(request, 'core/ratelimit_error.html', {
        'title': 'Too Many Requests',
        'message': 'You have made too many requests. Please wait a moment and try again.'
    }, status=429)
