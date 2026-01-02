from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, models
from django.db.models import F
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal
import json
import stripe
import hashlib
import time
from .models import MenuItem, Product, ProductCategory, Service, Quote, FAQ, Industry, Cart, CartItem, Order, OrderItem, SiteSettings, PromoCode, ProductReview
from .security import sanitize_text, sanitize_form_data, ratelimit_contact_form, ratelimit_quote_form, ratelimit_cart_api, handle_ratelimit
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


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


# =============================================================================
# CUSTOM ERROR HANDLERS
# =============================================================================
def custom_404_view(request, exception=None):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)


def custom_403_view(request, exception=None):
    """Custom 403 forbidden page"""
    return render(request, '403.html', status=403)


def custom_500_view(request):
    """Custom 500 server error page"""
    return render(request, '500.html', status=500)


def build_shipping_methods(cart):
    """Construct shipping method options with dynamic pricing."""
    from decimal import Decimal

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
    from decimal import Decimal

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


@handle_ratelimit
@ratelimit_contact_form
def index(request):
    if request.method == 'POST':
        # Handle contact form submission - sanitize inputs
        name = sanitize_text(request.POST.get('name', ''))
        email = sanitize_text(request.POST.get('email', ''))
        phone = sanitize_text(request.POST.get('phone', 'Not provided'))
        company = sanitize_text(request.POST.get('company', 'Not provided'))
        message_text = sanitize_text(request.POST.get('message', ''))
        
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

@handle_ratelimit
@ratelimit_contact_form
def contact_page(request):
    """Display contact page with form handling"""
    if request.method == 'POST':
        # Sanitize all form inputs
        name = sanitize_text(request.POST.get('name', ''))
        email = sanitize_text(request.POST.get('email', ''))
        phone = sanitize_text(request.POST.get('phone', 'Not provided'))
        company = sanitize_text(request.POST.get('company', 'Not provided'))
        subject = sanitize_text(request.POST.get('subject', 'Contact Form'))
        message_text = sanitize_text(request.POST.get('message', ''))
        
        try:
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                logger.warning('Email credentials not configured')
                messages.warning(
                    request,
                    'Your message has been received but email notifications are not configured. We will respond as soon as possible.'
                )
            else:
                email_subject = f'[Contact Form] {subject} - from {name}'
                email_body = f"""
New contact form submission from packaxis.ca/contact/

Subject: {subject}

Name: {name}
Email: {email}
Phone: {phone}
Company: {company}

Message:
{message_text}

---
This email was sent from the Packaxis website contact form.
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
                    'Thank you for contacting us! We\'ve received your message and will get back to you within 24 hours.'
                )
        except Exception as e:
            logger.error(f'Contact form email send failed: {str(e)}')
            messages.error(
                request,
                'Oops! Something went wrong. Please try again or contact us directly at hello@packaxis.ca'
            )
        
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')

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
    """Display all products on a dedicated page"""
    products = Product.objects.filter(is_active=True).select_related('category').order_by('category', 'title')
    categories = ProductCategory.objects.filter(is_active=True)
    
    # Get selected category filter
    selected_category = request.GET.get('category', '')
    if selected_category:
        products = products.filter(category__slug=selected_category)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
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

def category_detail(request, slug):
    """Category detail page showing all products in a category"""
    category = get_object_or_404(ProductCategory, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True).order_by('order', 'title')
    
    # Get tiered prices for displaying price range
    for product in products:
        if hasattr(product, 'tiered_prices'):
            product.tiered_prices_list = product.tiered_prices.all().order_by('min_quantity')
    
    context = {
        'category': category,
        'products': products,
        'product_categories': ProductCategory.objects.filter(is_active=True),
    }
    return render(request, 'core/category-detail.html', context)

def product_detail(request, category_slug, product_slug):
    """Dynamic product detail view using category and product slugs"""
    category = get_object_or_404(ProductCategory, slug=category_slug, is_active=True)
    product = get_object_or_404(Product, slug=product_slug, category=category, is_active=True)
    
    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get tiered pricing
    tiered_prices = []
    if hasattr(product, 'tiered_prices'):
        tiered_prices = product.tiered_prices.all().order_by('min_quantity')
    
    # Get product variants
    size_variants = []
    color_variants = []
    if hasattr(product, 'variants'):
        size_variants = product.variants.filter(variant_type='size', is_active=True)
        color_variants = product.variants.filter(variant_type='color', is_active=True)
    
    # Get approved reviews
    reviews = []
    if hasattr(product, 'reviews'):
        reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Get product industries
    product_industries = []
    if hasattr(product, 'product_industries'):
        product_industries = product.product_industries.select_related('industry').all()
    
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
        'tiered_prices': tiered_prices,
        'size_variants': size_variants,
        'color_variants': color_variants,
        'reviews': reviews,
        'product_industries': product_industries,
    }
    return render(request, 'core/product-detail.html', context)


@handle_ratelimit
@ratelimit_quote_form
def quote_request(request):
    """Quote request page with form"""
    product_categories = ProductCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            # Get and sanitize form data
            name = sanitize_text(request.POST.get('name', ''))
            company_name = sanitize_text(request.POST.get('company_name', ''))
            email = sanitize_text(request.POST.get('email', ''))
            contact_number = sanitize_text(request.POST.get('contact_number', ''))
            product_id = request.POST.get('product')
            size = sanitize_text(request.POST.get('size', ''))
            gsm = sanitize_text(request.POST.get('gsm', ''))
            quantity = request.POST.get('quantity')
            message_text = sanitize_text(request.POST.get('message', ''))
            
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


# Dynamic Industry-Specific Landing Pages
def industry_detail(request, slug):
    """
    Dynamic industry detail page that shows products for that industry.
    Uses the same template as category-detail.html for consistent layout.
    """
    # Convert slug to match industry URL field or title
    # E.g., 'restaurant-paper-bags' -> look for industry with url containing 'restaurant'
    slug_keyword = slug.split('-')[0]  # Get first word (e.g., 'restaurant' from 'restaurant-paper-bags')
    
    try:
        industry = Industry.objects.filter(is_active=True).get(
            models.Q(url__icontains=slug) | models.Q(title__icontains=slug_keyword)
        )
    except Industry.DoesNotExist:
        raise Http404(f"Industry '{slug}' not found")
    
    # Get products linked to this industry
    products = Product.objects.filter(
        is_active=True,
        industries__title__icontains=slug_keyword
    ).select_related('category').prefetch_related('additional_images', 'tiered_prices').distinct()
    
    # If no products are linked, show all products
    if not products.exists():
        products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('additional_images', 'tiered_prices').order_by('order')
    
    # Use same context variable name as category-detail for template compatibility
    context = {
        'category': industry,  # Renamed to 'category' to reuse category-detail.html template
        'products': products,
    }
    return render(request, 'core/category-detail.html', context)


# Legacy Industry-Specific Landing Pages (kept for backward compatibility)
def restaurant_paper_bags(request):
    # Get products linked to restaurant industry, or all products if none are linked
    industry_products = Product.objects.filter(
        is_active=True,
        industries__title__icontains='restaurant'
    ).select_related('category').prefetch_related('additional_images', 'tiered_prices').distinct()
    
    # If no products are linked to this industry, show all products
    if not industry_products.exists():
        industry_products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('additional_images', 'tiered_prices').order_by('order')
    
    context = {
        'products': industry_products,
        'industry': 'restaurant',
        'title': 'Restaurant Paper Bags',
        'subtitle': 'Food-Safe, Grease-Resistant Paper Bags for Restaurants & Takeout',
        'description': 'Premium paper bags designed specifically for restaurants, cafes, and food service businesses. FDA-approved, grease-resistant, and perfect for takeout orders.',
    }
    return render(request, 'core/industry-pages/restaurant.html', context)

def retail_paper_bags(request):
    industry_products = Product.objects.filter(
        is_active=True,
        industries__title__icontains='retail'
    ).select_related('category').prefetch_related('additional_images', 'tiered_prices').distinct()
    
    if not industry_products.exists():
        industry_products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('additional_images', 'tiered_prices').order_by('order')
    
    context = {
        'products': industry_products,
        'industry': 'retail',
        'title': 'Retail Paper Bags',
        'subtitle': 'Custom Branded Shopping Bags for Retail Stores',
        'description': 'Elevate your retail brand with custom paper shopping bags. Perfect for clothing stores, gift shops, and retail businesses across Canada.',
    }
    return render(request, 'core/industry-pages/retail.html', context)

def boutique_packaging(request):
    industry_products = Product.objects.filter(
        is_active=True,
        industries__title__icontains='boutique'
    ).select_related('category').prefetch_related('additional_images', 'tiered_prices').distinct()
    
    if not industry_products.exists():
        industry_products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('additional_images', 'tiered_prices').order_by('order')
    
    context = {
        'products': industry_products,
        'industry': 'boutique',
        'title': 'Boutique Packaging',
        'subtitle': 'Premium Luxury Paper Bags for High-End Boutiques',
        'description': 'Luxury paper bags that reflect your boutique\'s premium brand. Custom designs, premium finishes, and elegant presentation for fashion boutiques and specialty stores.',
    }
    return render(request, 'core/industry-pages/boutique.html', context)

def grocery_paper_bags(request):
    industry_products = Product.objects.filter(
        is_active=True,
        industries__title__icontains='grocery'
    ).select_related('category').prefetch_related('additional_images', 'tiered_prices').distinct()
    
    if not industry_products.exists():
        industry_products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('additional_images', 'tiered_prices').order_by('order')
    
    context = {
        'products': industry_products,
        'industry': 'grocery',
        'title': 'Grocery Paper Bags',
        'subtitle': 'Heavy-Duty Paper Bags for Grocery Stores & Supermarkets',
        'description': 'Strong, reliable paper bags for groceries and bulk items. Reinforced handles and sturdy construction perfect for supermarkets, farmers markets, and grocery stores.',
    }
    return render(request, 'core/industry-pages/grocery.html', context)

def bakery_paper_bags(request):
    industry_products = Product.objects.filter(
        is_active=True,
        industries__title__icontains='bakery'
    ).select_related('category').prefetch_related('additional_images', 'tiered_prices').distinct()
    
    if not industry_products.exists():
        industry_products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('additional_images', 'tiered_prices').order_by('order')
    
    context = {
        'products': industry_products,
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
    """Display shopping cart with tiered pricing"""
    cart = get_or_create_cart(request)
    
    # Prefetch products and their tiered prices for better performance
    cart_items = cart.items.select_related('product').prefetch_related('product__tiered_prices').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'core/cart.html', context)


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
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to access this invoice.")
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'core/invoice.html', context)


def send_order_confirmation_email(order):
    """Send order confirmation to customer"""
    try:
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
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
        
        from django.core.mail import EmailMultiAlternatives
        
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
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
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


# ============================================
# PROMO CODE VIEWS
# ============================================

@require_POST
def apply_promo_code(request):
    """Validate and apply a promo code to the cart session"""
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        email = data.get('email', '').strip()
        
        if not code:
            return JsonResponse({'success': False, 'error': 'Please enter a promo code.'})
        
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


# ============================================
# STRIPE PAYMENT VIEWS
# ============================================

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


@require_POST
def submit_review(request, category_slug, product_slug):
    """Submit a product review - only for customers who have purchased and received the product"""
    try:
        # Check authentication first for AJAX requests
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Please log in to submit a review.'
            }, status=401)
        
        product = get_object_or_404(Product, slug=product_slug, is_active=True)
        
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
        
    except Exception as e:
        logger.error(f'Review submission error: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'error': f'Failed to submit review: {str(e)}'}, status=500)

