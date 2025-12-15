from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json
from .models import MenuItem, Product, ProductCategory, Service, Quote, FAQ, Industry, Cart, CartItem, Order, OrderItem
import logging

logger = logging.getLogger(__name__)

def index(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', 'Not provided')
        company = request.POST.get('company', 'Not provided')
        message_text = request.POST.get('message')
        
        # Send email notification
        try:
            # Check if email is configured
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                logger.warning('Email credentials not configured')
                messages.warning(
                    request,
                    'Your message has been received but email notifications are not configured. We will respond as soon as possible.'
                )
            else:
                email_subject = f'New Contact Form Submission from {name}'
                email_body = f"""
                New contact form submission:
                
                Name: {name}
                Email: {email}
                Phone: {phone}
                Company: {company}
                
                Message:
                {message_text}
                """
                
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.QUOTE_EMAIL],
                    fail_silently=False,
                )
                
                messages.success(
                    request, 
                    'Thank you for reaching out! We\'ve received your message and will get back to you within 24 hours.'
                )
        except Exception as e:
            logger.error(f'Email send failed: {str(e)}')
            messages.error(
                request,
                'Oops! Something went wrong. Please try again or contact us directly at hello@packaxis.ca'
            )
        
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/#contact')
    
    product_categories = ProductCategory.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    industries = Industry.objects.filter(is_active=True).exclude(image='')
    context = {
        'product_categories': product_categories,
        'services': services,
        'industries': industries
    }
    return render(request, 'core/index.html', context)

def privacy_policy(request):
    return render(request, 'core/privacy-policy.html')

def services_page(request):
    """Display all services on a dedicated page"""
    services = Service.objects.filter(is_active=True)
    context = {
        'services': services,
    }
    return render(request, 'core/services.html', context)

def industries_page(request):
    """Display all industries on a dedicated page"""
    industries = Industry.objects.filter(is_active=True)
    context = {
        'industries': industries,
    }
    return render(request, 'core/industries.html', context)

def products_page(request):
    """Display all product categories on a dedicated page"""
    product_categories = ProductCategory.objects.filter(is_active=True)
    context = {
        'product_categories': product_categories,
    }
    return render(request, 'core/products.html', context)

def pricing_brochure(request):
    """Display pricing brochure for square bottom paper bags"""
    return render(request, 'core/pricing-brochure.html')


def faq(request):
    """Display FAQ page with common questions"""
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'core/faq.html', {'faqs': faqs})


def terms_of_service(request):
    return render(request, 'core/terms-of-service.html')

def brown_kraft_bags(request):
    context = {
        'product_name': 'Brown Kraft Bags',
        'category': 'Grocery & Food Packaging',
        'product_description': 'Classic eco-friendly brown kraft bags for groceries, food service, and general retail use. Strong, reliable, and environmentally responsible.',
        'product_image': 'images/assests/products/Brown Kraft Bag.jpg',
        'specifications': [
            {'title': 'Material', 'description': 'Natural Brown Kraft Paper'},
            {'title': 'GSM Range', 'description': '80-250 GSM'},
            {'title': 'Handle Type', 'description': 'Flat Paper Handles'},
            {'title': 'Food Safe', 'description': 'Yes - FDA Approved'},
        ],
        'features': [
            'Food-safe and hygienic',
            'Natural unbleached paper',
            'Eco-friendly and sustainable',
            'Perfect for groceries and food',
            'Cost-effective bulk pricing',
            'Custom printing available',
        ]
    }
    return render(request, 'core/product-detail.html', context)

def white_paper_bags(request):
    context = {
        'product_name': 'White Paper Bags',
        'category': 'Premium Retail Packaging',
        'product_description': 'Professional white paper bags perfect for bakeries, boutiques, and high-end retail. Clean, elegant, and ideal for brand customization.',
        'product_image': 'images/assests/products/White Paper Bag.jpg',
        'specifications': [
            {'title': 'Material', 'description': 'Bleached White Kraft Paper'},
            {'title': 'GSM Range', 'description': '100-300 GSM'},
            {'title': 'Handle Type', 'description': 'Flat/Twisted Paper Handles'},
            {'title': 'Finish', 'description': 'Smooth White Finish'},
        ],
        'features': [
            'Premium white appearance',
            'Perfect for bakeries and cafes',
            'Excellent print quality for logos',
            'Food-grade certified',
            'Professional and elegant',
            'Multiple size options',
        ]
    }
    return render(request, 'core/product-detail.html', context)

def custom_branded_bags(request):
    context = {
        'product_name': 'Custom Branded Bags',
        'category': 'Luxury Custom Packaging',
        'product_description': 'Fully customizable premium paper bags with your brand logo, colors, and designs. Perfect for events, luxury retail, and brand promotions.',
        'product_image': 'images/assests/products/Custom Paper Bag.jpg',
        'specifications': [
            {'title': 'Material', 'description': 'Choice of Kraft or Coated Paper'},
            {'title': 'Printing', 'description': 'Full Color CMYK Printing'},
            {'title': 'Handle Type', 'description': 'Rope, Ribbon, or Paper Handles'},
            {'title': 'Customization', 'description': 'Complete Design Freedom'},
        ],
        'features': [
            'Full custom design and branding',
            'High-quality printing',
            'Premium materials available',
            'Perfect for events and gifting',
            'Low minimum order quantities',
            'Professional design support',
        ]
    }
    return render(request, 'core/product-detail.html', context)

def paper_straws(request):
    context = {
        'product_name': 'Paper Straws',
        'category': 'Eco-Friendly Accessories',
        'product_description': 'Sustainable paper straws as an eco-friendly alternative to plastic. Perfect for restaurants, cafes, and events.',
        'product_image': 'images/assests/products/Paper Straw.jpg',
        'specifications': [
            {'title': 'Material', 'description': 'Food-Grade Paper'},
            {'title': 'Length', 'description': '197mm (7.75 inches)'},
            {'title': 'Diameter', 'description': '6mm Standard'},
            {'title': 'Colors', 'description': 'Plain or Striped'},
        ],
        'features': [
            '100% biodegradable',
            'FDA approved food-safe',
            'Durable in liquids',
            'Plain and striped options',
            'Bulk pricing available',
            'Perfect for eco-conscious businesses',
        ]
    }
    return render(request, 'core/product-detail.html', context)

def privacy_policy(request):
    return render(request, 'core/privacy-policy.html')

def terms_of_service(request):
    return render(request, 'core/terms-of-service.html')

def product_detail(request, slug):
    """Dynamic product detail view using slug"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'product_name': product.title,
        'category': product.category,
        'product_description': product.description,
        'product_image': product.image.url if product.image else '',
        'product_images': product.get_all_images(),
        'specifications': product.get_specifications(),
        'features': product.get_features(),
        'related_products': related_products,
    }
    return render(request, 'core/product-detail.html', context)


def quote_request(request):
    """Quote request page with form"""
    product_categories = ProductCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            company_name = request.POST.get('company_name', '')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            product_id = request.POST.get('product')
            size = request.POST.get('size')
            gsm = request.POST.get('gsm')
            quantity = request.POST.get('quantity')
            message_text = request.POST.get('message', '')
            
            # Get product object
            product = get_object_or_404(Product, id=product_id)
            
            # Create quote request
            quote = Quote.objects.create(
                name=name,
                company_name=company_name,
                email=email,
                contact_number=contact_number,
                product=product,
                size=size,
                gsm=gsm,
                quantity=int(quantity),
                message=message_text
            )
            
            # Send email notification
            subject = f'New Quote Request from {name}'
            email_message = f"""
New Quote Request Received:

Customer Details:
- Name: {name}
- Company: {company_name if company_name else 'N/A'}
- Email: {email}
- Phone: {contact_number}

Product Details:
- Product: {product.title}
- Size: {size}
- GSM: {gsm}
- Quantity: {quantity}

Additional Message:
{message_text if message_text else 'None'}

Quote ID: {quote.id}
Submitted: {quote.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            try:
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.QUOTE_EMAIL],  # Email where quotes should be sent
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            messages.success(request, '🎉 Thank you! Your quote request has been submitted successfully. We\'ll get back to you within 24 hours.')
            return redirect('core:quote_request')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}. Please try again or contact us directly.')
    
    context = {
        'product_categories': product_categories,
    }
    return render(request, 'core/quote.html', context)

# Industry-Specific Landing Pages
def restaurant_paper_bags(request):
    product_categories = ProductCategory.objects.filter(is_active=True).order_by('order')
    context = {
        'product_categories': product_categories,
        'industry': 'restaurant',
        'title': 'Restaurant Paper Bags',
        'subtitle': 'Food-Safe, Grease-Resistant Paper Bags for Restaurants & Takeout',
        'description': 'Premium paper bags designed specifically for restaurants, cafes, and food service businesses. FDA-approved, grease-resistant, and perfect for takeout orders.',
    }
    return render(request, 'core/industry-pages/restaurant.html', context)

def retail_paper_bags(request):
    product_categories = ProductCategory.objects.filter(is_active=True).order_by('order')
    context = {
        'product_categories': product_categories,
        'industry': 'retail',
        'title': 'Retail Paper Bags',
        'subtitle': 'Custom Branded Shopping Bags for Retail Stores',
        'description': 'Elevate your retail brand with custom paper shopping bags. Perfect for clothing stores, gift shops, and retail businesses across Canada.',
    }
    return render(request, 'core/industry-pages/retail.html', context)

def boutique_packaging(request):
    product_categories = ProductCategory.objects.filter(is_active=True).order_by('order')
    context = {
        'product_categories': product_categories,
        'industry': 'boutique',
        'title': 'Boutique Packaging',
        'subtitle': 'Premium Luxury Paper Bags for High-End Boutiques',
        'description': 'Luxury paper bags that reflect your boutique\'s premium brand. Custom designs, premium finishes, and elegant presentation for fashion boutiques and specialty stores.',
    }
    return render(request, 'core/industry-pages/boutique.html', context)

def grocery_paper_bags(request):
    product_categories = ProductCategory.objects.filter(is_active=True).order_by('order')
    context = {
        'product_categories': product_categories,
        'industry': 'grocery',
        'title': 'Grocery Paper Bags',
        'subtitle': 'Heavy-Duty Paper Bags for Grocery Stores & Supermarkets',
        'description': 'Strong, reliable paper bags for groceries and bulk items. Reinforced handles and sturdy construction perfect for supermarkets, farmers markets, and grocery stores.',
    }
    return render(request, 'core/industry-pages/grocery.html', context)

def bakery_paper_bags(request):
    product_categories = ProductCategory.objects.filter(is_active=True).order_by('order')
    context = {
        'product_categories': product_categories,
        'industry': 'bakery',
        'title': 'Bakery Paper Bags',
        'subtitle': 'Food-Grade Paper Bags for Bakeries, Cafes & Pastry Shops',
        'description': 'Grease-resistant paper bags perfect for baked goods, pastries, and bread. FDA-approved materials safe for direct food contact with custom branding options.',
    }
    return render(request, 'core/industry-pages/bakery.html', context)


# ============================================
# E-COMMERCE / CART VIEWS
# ============================================

def get_or_create_cart(request):
    """Get or create a cart for the current session"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    """Display shopping cart"""
    cart = get_or_create_cart(request)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
    }
    return render(request, 'core/cart.html', context)


def add_to_cart(request, slug):
    """Add a product to cart"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = get_or_create_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock if tracking inventory
    if product.track_inventory and not product.allow_backorder:
        if product.stock_quantity < quantity:
            messages.error(request, f'Sorry, only {product.stock_quantity} items available in stock.')
            return redirect('core:product_detail', slug=slug)
    
    # Check minimum order quantity
    if product.minimum_order and quantity < product.minimum_order:
        messages.warning(request, f'Minimum order quantity is {product.minimum_order} items.')
        quantity = product.minimum_order
    
    # Add to cart or update quantity
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Updated quantity of "{product.title}" in your cart.')
    else:
        messages.success(request, f'Added "{product.title}" to your cart.')
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Added {quantity}x {product.title} to cart',
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })
    
    return redirect('core:cart')


@require_POST
def update_cart(request):
    """Update cart item quantity"""
    cart = get_or_create_cart(request)
    
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity <= 0:
            cart_item.delete()
            message = f'Removed "{cart_item.product.title}" from cart.'
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
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'item_total': str(cart_item.total_price) if quantity > 0 else '0',
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


def checkout(request):
    """Checkout page with order form"""
    cart = get_or_create_cart(request)
    
    # Redirect to cart if empty
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty. Add some products before checkout.')
        return redirect('core:cart')
    
    if request.method == 'POST':
        try:
            # Create order from cart
            order = Order.objects.create(
                email=request.POST.get('email'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                company_name=request.POST.get('company_name', ''),
                phone=request.POST.get('phone'),
                shipping_address_1=request.POST.get('shipping_address_1'),
                shipping_address_2=request.POST.get('shipping_address_2', ''),
                shipping_city=request.POST.get('shipping_city'),
                shipping_state=request.POST.get('shipping_state'),
                shipping_postal_code=request.POST.get('shipping_postal_code'),
                shipping_country=request.POST.get('shipping_country', 'Canada'),
                customer_notes=request.POST.get('customer_notes', ''),
                subtotal=cart.subtotal,
                total=cart.total,
            )
            
            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_title=cart_item.product.title,
                    product_sku=cart_item.product.sku or '',
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    total_price=cart_item.total_price,
                )
                
                # Update stock if tracking
                if cart_item.product.track_inventory:
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()
            
            # Send order confirmation email
            send_order_confirmation_email(order)
            
            # Send notification to admin
            send_order_notification_email(order)
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('core:order_confirmation', order_number=order.order_number)
            
        except Exception as e:
            logger.error(f'Checkout error: {str(e)}')
            messages.error(request, 'An error occurred during checkout. Please try again.')
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
    }
    return render(request, 'core/checkout.html', context)


def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'core/order-confirmation.html', context)


def send_order_confirmation_email(order):
    """Send order confirmation to customer"""
    try:
        subject = f'Order Confirmation - {order.order_number}'
        
        items_text = '\n'.join([
            f"  - {item.product_title} x {item.quantity} @ ${item.unit_price} = ${item.total_price}"
            for item in order.items.all()
        ])
        
        message = f"""
Thank you for your order!

Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}

Order Details:
{items_text}

Subtotal: ${order.subtotal}
Shipping: ${order.shipping_cost}
Tax: ${order.tax}
Total: ${order.total}

Shipping Address:
{order.full_name}
{order.shipping_address}

We'll notify you when your order ships.

Thank you for shopping with PackAxis!
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f'Failed to send order confirmation email: {str(e)}')


def send_order_notification_email(order):
    """Send new order notification to admin"""
    try:
        subject = f'New Order Received - {order.order_number}'
        
        items_text = '\n'.join([
            f"  - {item.product_title} x {item.quantity} @ ${item.unit_price} = ${item.total_price}"
            for item in order.items.all()
        ])
        
        message = f"""
New Order Received!

Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}

Customer Information:
- Name: {order.full_name}
- Email: {order.email}
- Phone: {order.phone}
- Company: {order.company_name or 'N/A'}

Order Details:
{items_text}

Subtotal: ${order.subtotal}
Shipping: ${order.shipping_cost}
Tax: ${order.tax}
Total: ${order.total}

Shipping Address:
{order.shipping_address}

Customer Notes:
{order.customer_notes or 'None'}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.QUOTE_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f'Failed to send order notification email: {str(e)}')
