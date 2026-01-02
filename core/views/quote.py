"""
Quote request view.
Includes: quote form, quote submission, validation.
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from ..models import Product, ProductCategory, Quote
from ..security import sanitize_text, ratelimit_quote_form, handle_ratelimit

logger = logging.getLogger(__name__)


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
