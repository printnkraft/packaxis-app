"""
Security utilities for PackAxis
- Rate limiting decorators
- Input sanitization functions
- Security helpers
"""
import bleach
from functools import wraps
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited


# Allowed HTML tags and attributes for sanitization
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
]
ALLOWED_ATTRIBUTES = {}


def sanitize_html(text):
    """
    Sanitize HTML input to prevent XSS attacks.
    Strips all HTML tags except basic formatting.
    """
    if not text:
        return text
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def sanitize_text(text):
    """
    Completely strip all HTML tags from text.
    Use for fields that should never contain HTML.
    """
    if not text:
        return text
    return bleach.clean(text, tags=[], strip=True)


def sanitize_form_data(data, fields_to_sanitize=None, strip_all_html=False):
    """
    Sanitize multiple form fields at once.
    
    Args:
        data: Dictionary of form data
        fields_to_sanitize: List of field names to sanitize (None = all string fields)
        strip_all_html: If True, strips ALL HTML. If False, allows basic formatting.
    
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    sanitize_func = sanitize_text if strip_all_html else sanitize_html
    
    for key, value in data.items():
        if isinstance(value, str):
            if fields_to_sanitize is None or key in fields_to_sanitize:
                sanitized[key] = sanitize_func(value)
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value
    
    return sanitized


# Rate limiting decorators for common use cases
def ratelimit_contact_form(view_func):
    """
    Rate limit contact form submissions.
    5 submissions per minute per IP.
    """
    return ratelimit(key='ip', rate='5/m', method='POST', block=True)(view_func)


def ratelimit_quote_form(view_func):
    """
    Rate limit quote request submissions.
    3 submissions per minute per IP.
    """
    return ratelimit(key='ip', rate='3/m', method='POST', block=True)(view_func)


def ratelimit_cart_api(view_func):
    """
    Rate limit cart API operations.
    30 requests per minute per IP.
    """
    return ratelimit(key='ip', rate='30/m', method=['POST', 'GET'], block=True)(view_func)


def ratelimit_checkout(view_func):
    """
    Rate limit checkout attempts.
    10 attempts per minute per IP.
    """
    return ratelimit(key='ip', rate='10/m', method='POST', block=True)(view_func)


def ratelimit_login(view_func):
    """
    Rate limit login attempts.
    5 attempts per minute per IP.
    """
    return ratelimit(key='ip', rate='5/m', method='POST', block=True)(view_func)


def ratelimit_search(view_func):
    """
    Rate limit search requests.
    20 requests per minute per IP.
    """
    return ratelimit(key='ip', rate='20/m', method='GET', block=True)(view_func)


def handle_ratelimit(view_func):
    """
    Decorator to handle rate limit exceptions gracefully.
    Returns appropriate JSON or HTML response when rate limited.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Ratelimited:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Too many requests. Please wait a moment and try again.',
                    'rate_limited': True
                }, status=429)
            # For regular requests, let Django handle it
            raise
    return wrapper


# Combined decorator for form views
def secure_form_view(rate='5/m'):
    """
    Combined decorator for form views that applies:
    - Rate limiting
    - Graceful error handling
    
    Usage:
        @secure_form_view(rate='5/m')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @handle_ratelimit
        @ratelimit(key='ip', rate=rate, method='POST', block=True)
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
