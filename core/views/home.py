"""
Home and static page views.
Includes: homepage, contact, privacy, terms, services, industries, products, pricing, FAQ.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect
import logging
from ..models import ProductCategory, Service, Industry, Product, FAQ
from ..security import sanitize_text, ratelimit_contact_form, handle_ratelimit

logger = logging.getLogger(__name__)


@handle_ratelimit
@ratelimit_contact_form
def index(request):
    """Homepage with contact form"""
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
    """Privacy policy page"""
    return render(request, 'core/privacy-policy.html')


def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'core/terms-of-service.html')


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
