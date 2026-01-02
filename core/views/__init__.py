"""
Views package.

This package organizes all views into focused modules for better maintainability and scalability.

Modules:
- home.py: Homepage and static pages (index, contact, privacy, terms, services, industries, products, pricing, faq)
- catalog.py: Product catalog (categories, products, legacy landing pages)
- industry.py: Industry-specific pages
- cart.py: Shopping cart operations (add, update, remove, display)
- checkout.py: Checkout process and order management
- payment.py: Stripe payment processing
- quote.py: Quote request handling
- api.py: AJAX API endpoints (promo codes, reviews, rate limiting)
- utils.py: Shared utility functions (cart validation, shipping, calculations)
"""

# Home and static pages
from .home import (
    index,
    privacy_policy,
    terms_of_service,
    contact_page,
    services_page,
    industries_page,
    products_page,
    pricing_brochure,
    faq,
)

# Product catalog
from .catalog import (
    category_detail,
    product_detail,
    brown_kraft_bags,
    white_paper_bags,
    custom_branded_bags,
    paper_straws,
)

# Industry pages
from .industry import (
    industry_detail,
    restaurant_paper_bags,
)

# Shopping cart
from .cart import (
    get_or_create_cart,
    cart_view,
    add_to_cart,
    update_cart,
    remove_from_cart,
    update_cart_ajax,
    remove_cart_ajax,
    set_cart_quantity_ajax,
    cart_dropdown_html,
)

# Checkout and orders
from .checkout import (
    checkout,
    order_confirmation,
    download_invoice,
    send_order_confirmation_email,
    send_order_notification_email,
)

# Payment processing
from .payment import (
    create_payment_intent,
    process_payment,
    stripe_webhook,
)

# Quote requests
from .quote import (
    quote_request,
)

# API endpoints
from .api import (
    apply_promo_code,
    remove_promo_code,
    submit_review,
    ratelimit_error,
)

# Utility functions
from .utils import (
    generate_idempotency_key,
    validate_cart_for_checkout,
    build_shipping_methods,
    calculate_order_totals,
)

__all__ = [
    # Home
    'index',
    'privacy_policy',
    'terms_of_service',
    'contact_page',
    'services_page',
    'industries_page',
    'products_page',
    'pricing_brochure',
    'faq',
    # Catalog
    'category_detail',
    'product_detail',
    'brown_kraft_bags',
    'white_paper_bags',
    'custom_branded_bags',
    'paper_straws',
    # Industry
    'industry_detail',
    'restaurant_paper_bags',
    # Cart
    'get_or_create_cart',
    'cart_view',
    'add_to_cart',
    'update_cart',
    'remove_from_cart',
    'update_cart_ajax',
    'remove_cart_ajax',
    'set_cart_quantity_ajax',
    'cart_dropdown_html',
    # Checkout
    'checkout',
    'order_confirmation',
    'download_invoice',
    'send_order_confirmation_email',
    'send_order_notification_email',
    # Payment
    'create_payment_intent',
    'process_payment',
    'stripe_webhook',
    # Quote
    'quote_request',
    # API
    'apply_promo_code',
    'remove_promo_code',
    'submit_review',
    'ratelimit_error',
    # Utils
    'generate_idempotency_key',
    'validate_cart_for_checkout',
    'build_shipping_methods',
    'calculate_order_totals',
]
