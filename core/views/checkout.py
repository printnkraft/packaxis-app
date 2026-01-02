"""
Checkout and order management views.
Includes: checkout process, order confirmation, invoice download, order emails.
"""
import logging
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.core.cache import cache
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden
from ..models import Cart, Order, OrderItem, Product, PromoCode, SiteSettings
from ..security import sanitize_text
from .utils import (
    generate_idempotency_key,
    validate_cart_for_checkout,
    build_shipping_methods,
    calculate_order_totals,
)
from .cart import get_or_create_cart

logger = logging.getLogger(__name__)


def checkout(request):
    """Checkout page with order form"""
    cart = get_or_create_cart(request)
    
    # Redirect to cart if empty
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty. Add some products before checkout.')
        return redirect('core:cart')
    
    # Re-verify stock availability before checkout
    stock_errors = []
    for item in cart.items.select_related('product').all():
        if item.product.track_inventory and not item.product.allow_backorder:
            if item.product.stock_quantity < item.quantity:
                stock_errors.append(f'{item.product.title}: only {item.product.stock_quantity} available')
    
    if stock_errors:
        for error in stock_errors:
            messages.error(request, error)
        return redirect('core:cart')
    
    # Build shipping options and calculate totals up front for both GET/POST flows
    shipping_methods = build_shipping_methods(cart)
    if request.method == 'POST':
        selected_shipping_method_id = request.POST.get('shipping_method', shipping_methods[0]['id'])
        province_input = request.POST.get('shipping_state', '').strip().upper() or 'ON'
    else:
        selected_shipping_method_id = shipping_methods[0]['id']
        province_input = 'ON'

    order_totals = calculate_order_totals(
        cart,
        selected_shipping_method_id,
        province_input,
        shipping_methods,
    )

    if request.method == 'POST':
        # Server-side validation
        errors = []
        required_fields = ['first_name', 'last_name', 'email', 'phone', 
                          'shipping_address_1', 'shipping_city', 'shipping_state', 'shipping_postal_code']
        
        for field in required_fields:
            if not request.POST.get(field, '').strip():
                errors.append(f'{field.replace("_", " ").title()} is required')
        
        # Validate email format
        email = request.POST.get('email', '').strip()
        if email and '@' not in email:
            errors.append('Please enter a valid email address')

        valid_shipping_ids = {method['id'] for method in shipping_methods}
        if selected_shipping_method_id not in valid_shipping_ids:
            errors.append('Please select a valid shipping method')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Generate idempotency key to prevent duplicate submissions
            user_identifier = request.user.email if request.user.is_authenticated else request.session.session_key
            idempotency_key = generate_idempotency_key(cart.id, user_identifier)
            
            # Check for duplicate submission (within 5-minute window)
            cache_key = f'checkout_idempotency_{idempotency_key}'
            if cache.get(cache_key):
                messages.warning(request, 'Your order is being processed. Please wait...')
                return redirect('core:cart')
            
            try:
                # Handle promo code from form or session
                promo_code_str = request.POST.get('promo_code', '').strip().upper()
                if not promo_code_str:
                    promo_code_str = request.session.get('promo_code', '')
                
                discount_amount = Decimal('0.00')
                if promo_code_str:
                    try:
                        promo = PromoCode.objects.get(code=promo_code_str)
                        is_valid, _ = promo.is_valid(cart.subtotal, email)
                        if is_valid:
                            discount_amount = promo.calculate_discount(cart.subtotal, order_totals['shipping_cost'])
                            # Increment usage
                            PromoCode.objects.filter(id=promo.id).update(usage_count=F('usage_count') + 1)
                    except PromoCode.DoesNotExist:
                        promo_code_str = ''  # Invalid code
                
                # Recalculate total with discount
                final_subtotal = cart.subtotal - discount_amount
                final_tax = final_subtotal * Decimal(str(order_totals['tax_rate']))
                final_total = final_subtotal + order_totals['shipping_cost'] + final_tax
                
                # Use database transaction for order creation
                with transaction.atomic():
                    # Lock cart items to prevent race conditions
                    cart_items_locked = list(cart.items.select_related('product').select_for_update().all())
                    
                    # Final stock verification within transaction
                    for item in cart_items_locked:
                        if item.product.track_inventory and not item.product.allow_backorder:
                            # Refresh product to get current stock
                            current_stock = Product.objects.filter(id=item.product.id).values_list('stock_quantity', flat=True).first()
                            if current_stock < item.quantity:
                                raise ValueError(f'{item.product.title}: only {current_stock} available')
                    
                    # Check if different billing address
                    different_billing = request.POST.get('different_billing') == 'on'
                    
                    # Create order from cart
                    order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    email=email,
                    first_name=request.POST.get('first_name', '').strip(),
                    last_name=request.POST.get('last_name', '').strip(),
                    company_name=request.POST.get('company_name', '').strip(),
                    phone=request.POST.get('phone', '').strip(),
                    shipping_address_1=request.POST.get('shipping_address_1', '').strip(),
                    shipping_address_2=request.POST.get('shipping_address_2', '').strip(),
                    shipping_city=request.POST.get('shipping_city', '').strip(),
                    shipping_state=request.POST.get('shipping_state', '').strip(),
                    shipping_postal_code=request.POST.get('shipping_postal_code', '').strip().upper(),
                    shipping_country=request.POST.get('shipping_country', 'Canada').strip(),
                    shipping_method=order_totals['selected_method']['label'],
                    shipping_eta=order_totals['selected_method']['eta'],
                    # Billing address
                    billing_same_as_shipping=not different_billing,
                    billing_address_1=request.POST.get('billing_address_1', '').strip() if different_billing else '',
                    billing_address_2=request.POST.get('billing_address_2', '').strip() if different_billing else '',
                    billing_city=request.POST.get('billing_city', '').strip() if different_billing else '',
                    billing_state=request.POST.get('billing_state', '').strip() if different_billing else '',
                    billing_postal_code=request.POST.get('billing_postal_code', '').strip().upper() if different_billing else '',
                    billing_country=request.POST.get('billing_country', 'Canada').strip() if different_billing else '',
                    customer_notes=request.POST.get('customer_notes', '').strip(),
                    subtotal=cart.subtotal,
                    shipping_cost=order_totals['shipping_cost'],
                    tax=final_tax,
                    discount=discount_amount,
                    promo_code=promo_code_str,
                    total=final_total,
                )
                
                    # Create order items from locked cart items
                    for cart_item in cart_items_locked:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            product_title=cart_item.product.title,
                            product_sku=cart_item.product.sku or '',
                            quantity=cart_item.quantity,
                            unit_price=cart_item.unit_price,
                            total_price=cart_item.total_price,
                        )
                        
                        # Update stock atomically using F() to prevent race conditions
                        if cart_item.product.track_inventory:
                            Product.objects.filter(id=cart_item.product.id).update(
                                stock_quantity=F('stock_quantity') - cart_item.quantity
                            )
                    
                    # Clear cart within transaction
                    cart.items.all().delete()
                
                # Set idempotency cache after successful transaction (outside transaction)
                cache.set(cache_key, order.order_number, 300)  # 5 minutes
                
                # Send emails asynchronously (outside transaction)
                try:
                    send_order_confirmation_email(order)
                    send_order_notification_email(order)
                except Exception as email_error:
                    logger.error(f'Email send failed for order {order.order_number}: {str(email_error)}')
                
                # Store order number in session for access control
                recent_orders = request.session.get('recent_orders', [])
                recent_orders.append(order.order_number)
                request.session['recent_orders'] = recent_orders[-5:]
                
                # Clear promo code from session
                if 'promo_code' in request.session:
                    del request.session['promo_code']
                if 'promo_discount' in request.session:
                    del request.session['promo_discount']
                
                return redirect('core:order_confirmation', order_number=order.order_number)
                
            except ValueError as ve:
                logger.warning(f'Checkout validation error: {str(ve)}')
                messages.error(request, str(ve))
            except Exception as e:
                logger.error(f'Checkout error: {str(e)}')
                messages.error(request, 'An error occurred during checkout. Please try again.')
    
    # Get site settings
    site_settings = SiteSettings.get_settings()
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'online_payments_enabled': site_settings.online_payments_enabled,
        'order_totals': order_totals,
        'shipping_methods': shipping_methods,
        'selected_shipping_method_id': order_totals['selected_method']['id'],
        'selected_province': order_totals['province'],
        'tax_rates': {code: float(rate) for code, rate in cart.TAX_RATES.items()},
    }
    return render(request, 'core/checkout.html', context)


def order_confirmation(request, order_number):
    """Order confirmation page with security checks"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Security: Verify user has access to this order
    # Allow access if:
    # 1. User is authenticated and owns this order (linked user or matching email)
    # 2. Order was just placed (stored in session within last 30 minutes)
    # 3. User is staff/admin
    
    has_access = False
    
    if request.user.is_authenticated:
        if request.user.is_staff:
            has_access = True
        elif order.user == request.user:
            has_access = True
        elif order.email.lower() == request.user.email.lower():
            has_access = True
    
    # Check if order was recently placed by this session
    recent_orders = request.session.get('recent_orders', [])
    if order_number in recent_orders:
        has_access = True
    
    # Store order number in session for guest access
    if not has_access:
        # If no access, show generic "order received" without sensitive details
        logger.warning(f"Unauthorized order access attempt: {order_number} by {request.user if request.user.is_authenticated else 'anonymous'}")
        context = {
            'order': None,
            'order_number': order_number,
            'limited_access': True,
        }
        return render(request, 'core/order-confirmation.html', context)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'limited_access': False,
    }
    return render(request, 'core/order-confirmation.html', context)


def download_invoice(request, order_number):
    """Generate and download invoice as HTML/PDF with security checks"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Security: Verify user has access to this order
    has_access = False
    
    if request.user.is_authenticated:
        if request.user.is_staff:
            has_access = True
        elif order.user == request.user:
            has_access = True
        elif order.email.lower() == request.user.email.lower():
            has_access = True
    
    # Check if order was recently placed by this session
    recent_orders = request.session.get('recent_orders', [])
    if order_number in recent_orders:
        has_access = True
    
    if not has_access:
        logger.warning(f"Unauthorized invoice access attempt: {order_number} by {request.user if request.user.is_authenticated else 'anonymous'}")
        return HttpResponseForbidden("You do not have permission to access this invoice.")
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'core/invoice.html', context)


def send_order_confirmation_email(order):
    """Send order confirmation to customer"""
    try:
        subject = f'Order Confirmation - {order.order_number} | PackAxis'
        
        # Invoice URL
        invoice_url = f"https://packaxis.ca/invoice/{order.order_number}/"
        
        # Plain text version
        items_text = '\n'.join([
            f"  - {item.product_title} x {item.quantity} @ ${item.unit_price} = ${item.total_price}"
            for item in order.items.all()
        ])
        
        text_message = f"""
Thank you for your order!

Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}

Order Details:
{items_text}

Subtotal: ${order.subtotal}
Total: ${order.total}

Shipping Address:
{order.full_name}
{order.shipping_address}

View/Download Invoice: {invoice_url}

What's Next?
- Our team will review your order within 24 hours
- We'll contact you to confirm payment details
- You'll receive tracking info when your order ships

Thank you for shopping with PackAxis!

Questions? Reply to this email or call us at (416) 275-2227
        """
        
        # Render HTML from template
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'invoice_url': invoice_url,
        })
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f'Order confirmation email sent to {order.email} for order {order.order_number}')
        
    except Exception as e:
        logger.error(f'Failed to send order confirmation email to {order.email}: {str(e)}')


def send_order_notification_email(order):
    """Send new order notification to admin"""
    try:
        subject = f'🛒 New Order #{order.order_number} - ${order.total}'
        
        # Plain text version
        items_text = '\n'.join([
            f"  - {item.product_title} x {item.quantity} @ ${item.unit_price} = ${item.total_price}"
            for item in order.items.all()
        ])
        
        text_message = f"""
NEW ORDER RECEIVED!

Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}

CUSTOMER:
- Name: {order.full_name}
- Email: {order.email}
- Phone: {order.phone}
- Company: {order.company_name or 'N/A'}

ORDER ITEMS:
{items_text}

TOTALS:
- Subtotal: ${order.subtotal}
- Total: ${order.total}

SHIPPING ADDRESS:
{order.shipping_address}

CUSTOMER NOTES:
{order.customer_notes or 'None'}

---
Manage this order in the admin panel:
https://packaxis.ca/admin/core/order/
        """
        
        # Render HTML from template
        html_message = render_to_string('emails/order_notification.html', {
            'order': order,
        })
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.QUOTE_EMAIL],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f'Order notification email sent to admin for order {order.order_number}')
        
    except Exception as e:
        logger.error(f'Failed to send order notification email: {str(e)}')
