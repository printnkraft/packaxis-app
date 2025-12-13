from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import MenuItem, Product, Service, Quote, FAQ, Industry
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
    
    products = Product.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    industries = Industry.objects.filter(is_active=True).exclude(image='')
    context = {
        'products': products,
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

def products_page(request):
    """Display all products on a dedicated page"""
    products = Product.objects.filter(is_active=True)
    context = {
        'products': products,
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

def product_detail(request, slug):
    """Dynamic product detail view using slug"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    context = {
        'product': product,
        'product_name': product.title,
        'category': product.category,
        'product_description': product.description,
        'product_image': product.image.url if product.image else '',
        'specifications': product.get_specifications(),
        'features': product.get_features(),
    }
    return render(request, 'core/product-detail.html', context)
    context = {
        'product_name': 'Shopping Paper Bags',
        'category': 'Retail Packaging',
        'product_description': 'Premium kraft paper bags perfect for retail stores, boutiques, and shopping centers. Durable, eco-friendly, and customizable to match your brand.',
        'product_image': 'images/assests/products/Shopping Paper Bags.jpg',
        'specifications': [
            {'title': 'Material', 'description': 'Premium Kraft Paper'},
            {'title': 'GSM Range', 'description': '100-300 GSM'},
            {'title': 'Handle Type', 'description': 'Twisted/Flat Paper Handles'},
            {'title': 'Sizes', 'description': 'Multiple sizes available'},
        ],
        'features': [
            'Customizable with your logo and branding',
            '100% Recyclable and biodegradable',
            'Strong reinforced handles',
            'Ideal for retail and shopping',
            'Available in bulk quantities',
            'Fast turnaround time',
        ]
    }
    return render(request, 'core/product-detail.html', context)

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
    context = {
        'product': product,
        'product_name': product.title,
        'category': product.category,
        'product_description': product.description,
        'product_image': product.image.url if product.image else '',
        'specifications': product.get_specifications(),
        'features': product.get_features(),
    }
    return render(request, 'core/product-detail.html', context)


def quote_request(request):
    """Quote request page with form"""
    products = Product.objects.filter(is_active=True)
    
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
        'products': products,
    }
    return render(request, 'core/quote.html', context)

# Industry-Specific Landing Pages
def restaurant_paper_bags(request):
    products = Product.objects.filter(is_active=True).order_by('order')
    context = {
        'products': products,
        'industry': 'restaurant',
        'title': 'Restaurant Paper Bags',
        'subtitle': 'Food-Safe, Grease-Resistant Paper Bags for Restaurants & Takeout',
        'description': 'Premium paper bags designed specifically for restaurants, cafes, and food service businesses. FDA-approved, grease-resistant, and perfect for takeout orders.',
    }
    return render(request, 'core/industry-pages/restaurant.html', context)

def retail_paper_bags(request):
    products = Product.objects.filter(is_active=True).order_by('order')
    context = {
        'products': products,
        'industry': 'retail',
        'title': 'Retail Paper Bags',
        'subtitle': 'Custom Branded Shopping Bags for Retail Stores',
        'description': 'Elevate your retail brand with custom paper shopping bags. Perfect for clothing stores, gift shops, and retail businesses across Canada.',
    }
    return render(request, 'core/industry-pages/retail.html', context)

def boutique_packaging(request):
    products = Product.objects.filter(is_active=True).order_by('order')
    context = {
        'products': products,
        'industry': 'boutique',
        'title': 'Boutique Packaging',
        'subtitle': 'Premium Luxury Paper Bags for High-End Boutiques',
        'description': 'Luxury paper bags that reflect your boutique\'s premium brand. Custom designs, premium finishes, and elegant presentation for fashion boutiques and specialty stores.',
    }
    return render(request, 'core/industry-pages/boutique.html', context)

def grocery_paper_bags(request):
    products = Product.objects.filter(is_active=True).order_by('order')
    context = {
        'products': products,
        'industry': 'grocery',
        'title': 'Grocery Paper Bags',
        'subtitle': 'Heavy-Duty Paper Bags for Grocery Stores & Supermarkets',
        'description': 'Strong, reliable paper bags for groceries and bulk items. Reinforced handles and sturdy construction perfect for supermarkets, farmers markets, and grocery stores.',
    }
    return render(request, 'core/industry-pages/grocery.html', context)

def bakery_paper_bags(request):
    products = Product.objects.filter(is_active=True).order_by('order')
    context = {
        'products': products,
        'industry': 'bakery',
        'title': 'Bakery Paper Bags',
        'subtitle': 'Food-Grade Paper Bags for Bakeries, Cafes & Pastry Shops',
        'description': 'Grease-resistant paper bags perfect for baked goods, pastries, and bread. FDA-approved materials safe for direct food contact with custom branding options.',
    }
    return render(request, 'core/industry-pages/bakery.html', context)
