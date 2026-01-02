"""
Stripe payment processing views.
Includes: payment intent creation, payment processing, webhook handling.
"""
import json
import logging
import stripe
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.db.models import F
from ..models import Order, OrderItem, Product, Cart
from .utils import (
    generate_idempotency_key,
    build_shipping_methods,
    calculate_order_totals,
    validate_cart_for_checkout,
)
from .cart import get_or_create_cart
from .checkout import send_order_confirmation_email, send_order_notification_email

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@require_POST
def create_payment_intent(request):
    """Create a Stripe PaymentIntent for the checkout with proper totals calculation"""
    try:
        cart = get_or_create_cart(request)
        
        # Validate cart
        is_valid, validation_errors = validate_cart_for_checkout(cart)
        if not is_valid:
            return JsonResponse({'error': validation_errors[0]}, status=400)
        
        # Get shipping and tax info from request body for accurate total
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}
        
        shipping_method_id = data.get('shipping_method', 'standard')
        province = data.get('province', 'ON')
        
        # Calculate accurate totals including shipping and tax
        shipping_methods = build_shipping_methods(cart)
        order_totals = calculate_order_totals(cart, shipping_method_id, province, shipping_methods)
        
        # Calculate amount in cents (Stripe requires smallest currency unit)
        amount_cents = int(order_totals['grand_total'] * 100)
        
        # Generate idempotency key for Stripe
        user_identifier = request.user.email if request.user.is_authenticated else request.session.session_key
        stripe_idempotency_key = generate_idempotency_key(cart.id, f"{user_identifier}_intent")
        
        # Create PaymentIntent with idempotency key
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={'enabled': True},
            metadata={
                'cart_id': str(cart.id),
                'items_count': cart.total_items,
                'subtotal': str(cart.subtotal),
                'shipping_cost': str(order_totals['shipping_cost']),
                'tax_amount': str(order_totals['tax_amount']),
                'shipping_method': shipping_method_id,
                'province': province,
            },
            idempotency_key=stripe_idempotency_key,
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret,
            'amount': float(order_totals['grand_total']),
            'breakdown': {
                'subtotal': float(cart.subtotal),
                'shipping': float(order_totals['shipping_cost']),
                'tax': float(order_totals['tax_amount']),
                'total': float(order_totals['grand_total']),
            }
        })
        
    except stripe.error.StripeError as e:
        logger.error(f'Stripe error: {str(e)}')
        return JsonResponse({'error': str(e.user_message)}, status=400)
    except Exception as e:
        logger.error(f'Payment intent error: {str(e)}')
        return JsonResponse({'error': 'Failed to initialize payment'}, status=500)


@require_POST
def process_payment(request):
    """Process the payment after Stripe confirms it - with transaction safety"""
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        
        if not payment_intent_id:
            return JsonResponse({'error': 'Payment intent ID required'}, status=400)
        
        # Verify the payment with Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != 'succeeded':
            return JsonResponse({'error': 'Payment not completed'}, status=400)
        
        cart = get_or_create_cart(request)
        
        # Validate cart
        is_valid, validation_errors = validate_cart_for_checkout(cart)
        if not is_valid:
            return JsonResponse({'error': validation_errors[0]}, status=400)
        
        # Check for duplicate order with this payment intent
        existing_order = Order.objects.filter(payment_id=payment_intent_id).first()
        if existing_order:
            logger.info(f'Duplicate payment processing attempt for intent {payment_intent_id}')
            return JsonResponse({
                'success': True,
                'order_number': existing_order.order_number,
                'redirect_url': f'/order-confirmation/{existing_order.order_number}/'
            })
        
        # Get form data from the request
        form_data = data.get('form_data', {})
        
        # Calculate proper totals
        shipping_method_id = form_data.get('shipping_method', 'standard')
        province = form_data.get('shipping_state', 'ON').upper()
        shipping_methods = build_shipping_methods(cart)
        order_totals = calculate_order_totals(cart, shipping_method_id, province, shipping_methods)
        
        # Check if different billing address
        different_billing = form_data.get('different_billing', False)
        
        try:
            with transaction.atomic():
                # Lock cart items
                cart_items_locked = list(cart.items.select_related('product').select_for_update().all())
                
                # Final stock verification
                for item in cart_items_locked:
                    if item.product.track_inventory and not item.product.allow_backorder:
                        current_stock = Product.objects.filter(id=item.product.id).values_list('stock_quantity', flat=True).first()
                        if current_stock < item.quantity:
                            raise ValueError(f'{item.product.title}: only {current_stock} available')
                
                # Create order with proper totals
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    email=form_data.get('email', ''),
                    first_name=form_data.get('first_name', ''),
                    last_name=form_data.get('last_name', ''),
                    company_name=form_data.get('company_name', ''),
                    phone=form_data.get('phone', ''),
                    shipping_address_1=form_data.get('shipping_address_1', ''),
                    shipping_address_2=form_data.get('shipping_address_2', ''),
                    shipping_city=form_data.get('shipping_city', ''),
                    shipping_state=form_data.get('shipping_state', ''),
                    shipping_postal_code=form_data.get('shipping_postal_code', '').upper(),
                    shipping_country=form_data.get('shipping_country', 'Canada'),
                    shipping_method=order_totals['selected_method']['label'],
                    shipping_eta=order_totals['selected_method']['eta'],
                    # Billing address
                    billing_same_as_shipping=not different_billing,
                    billing_address_1=form_data.get('billing_address_1', '') if different_billing else '',
                    billing_address_2=form_data.get('billing_address_2', '') if different_billing else '',
                    billing_city=form_data.get('billing_city', '') if different_billing else '',
                    billing_state=form_data.get('billing_state', '') if different_billing else '',
                    billing_postal_code=form_data.get('billing_postal_code', '').upper() if different_billing else '',
                    billing_country=form_data.get('billing_country', 'Canada') if different_billing else '',
                    customer_notes=form_data.get('customer_notes', ''),
                    subtotal=cart.subtotal,
                    shipping_cost=order_totals['shipping_cost'],
                    tax=order_totals['tax_amount'],
                    total=order_totals['grand_total'],
                    # Payment info
                    payment_status='paid',
                    payment_method='stripe',
                    payment_id=payment_intent_id,
                )
                
                # Create order items
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
                    
                    # Update stock atomically
                    if cart_item.product.track_inventory:
                        Product.objects.filter(id=cart_item.product.id).update(
                            stock_quantity=F('stock_quantity') - cart_item.quantity
                        )
                
                # Clear cart
                cart.items.all().delete()
            
            # Store order in session (outside transaction)
            recent_orders = request.session.get('recent_orders', [])
            recent_orders.append(order.order_number)
            request.session['recent_orders'] = recent_orders[-5:]
            
            # Send emails (outside transaction, non-blocking)
            try:
                send_order_confirmation_email(order)
                send_order_notification_email(order)
            except Exception as email_error:
                logger.error(f'Email send failed for order {order.order_number}: {str(email_error)}')
            
            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'redirect_url': f'/order-confirmation/{order.order_number}/'
            })
            
        except ValueError as ve:
            logger.warning(f'Stripe payment stock error: {str(ve)}')
            return JsonResponse({'error': str(ve)}, status=400)
        
    except stripe.error.StripeError as e:
        logger.error(f'Stripe verification error: {str(e)}')
        return JsonResponse({'error': 'Payment verification failed'}, status=400)
    except Exception as e:
        logger.error(f'Process payment error: {str(e)}')
        return JsonResponse({'error': 'Failed to process order'}, status=500)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks for payment events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        return JsonResponse({'error': 'Webhook not configured'}, status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f'Invalid webhook payload: {str(e)}')
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f'Invalid webhook signature: {str(e)}')
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f'Payment succeeded: {payment_intent["id"]}')
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logger.warning(f'Payment failed: {payment_intent["id"]}')
        
        # Update order status if exists
        try:
            order = Order.objects.get(payment_id=payment_intent['id'])
            order.payment_status = 'failed'
            order.save()
        except Order.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'success'})
