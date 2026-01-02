# Phase 3: Views Module Reference Guide

## Quick Module Map

```
core/views/
├── home.py           → index, contact_page, privacy_policy, terms_of_service,
│                       services_page, industries_page, products_page, 
│                       pricing_brochure, faq
├── catalog.py        → category_detail, product_detail, brown_kraft_bags,
│                       white_paper_bags, custom_branded_bags, paper_straws
├── industry.py       → industry_detail, restaurant_paper_bags
├── cart.py           → add_to_cart, update_cart, remove_from_cart,
│                       cart_view, cart_dropdown_html, get_or_create_cart,
│                       update_cart_ajax, remove_cart_ajax, set_cart_quantity_ajax
├── checkout.py       → checkout, order_confirmation, download_invoice,
│                       send_order_confirmation_email, send_order_notification_email
├── payment.py        → create_payment_intent, process_payment, stripe_webhook
├── quote.py          → quote_request
├── api.py            → apply_promo_code, remove_promo_code, submit_review,
│                       ratelimit_error
├── utils.py          → generate_idempotency_key, validate_cart_for_checkout,
│                       build_shipping_methods, calculate_order_totals
└── __init__.py       → Re-exports all for backward compatibility
```

## View-by-Feature Lookup

### Homepage & Static Pages (home.py)
- `/` → `index()` - Homepage with contact form
- `/contact/` → `contact_page()` - Contact page
- `/privacy-policy/` → `privacy_policy()` - Privacy policy
- `/terms-of-service/` → `terms_of_service()` - Terms of service
- `/services/` → `services_page()` - Services listing
- `/industries/` → `industries_page()` - Industries listing
- `/products/` → `products_page()` - All products
- `/pricing-brochure/` → `pricing_brochure()` - Pricing page
- `/faq/` → `faq()` - FAQ page

### Product Catalog (catalog.py, industry.py)
- `/product/<slug>/` → `category_detail()` - Category page
- `/product/<cat_slug>/<prod_slug>/` → `product_detail()` - Product page
- `/<slug>/` → `industry_detail()` - Industry page
- `/restaurant-paper-bags/` → `restaurant_paper_bags()` - Legacy industry page
- Legacy product pages → `brown_kraft_bags()`, `white_paper_bags()`, etc.

### Shopping Cart (cart.py)
- `/cart/` → `cart_view()` - View cart
- `/cart/add/<slug>/` → `add_to_cart()` - Add product (POST)
- `/cart/update/` → `update_cart()` - Update quantity (POST)
- `/cart/remove/<id>/` → `remove_from_cart()` - Remove item
- `/cart/dropdown-html/` → `cart_dropdown_html()` - AJAX cart dropdown
- `/cart/update-ajax/<id>/` → `update_cart_ajax()` - AJAX quantity adjust
- `/cart/remove-ajax/<id>/` → `remove_cart_ajax()` - AJAX remove
- `/cart/set-quantity-ajax/<id>/` → `set_cart_quantity_ajax()` - AJAX set quantity

### Checkout & Orders (checkout.py, payment.py)
- `/checkout/` → `checkout()` - Checkout page (handles POST)
- `/order-confirmation/<order_num>/` → `order_confirmation()` - Order page
- `/invoice/<order_num>/` → `download_invoice()` - Invoice download
- `/payment/create-intent/` → `create_payment_intent()` - Stripe intent (AJAX)
- `/payment/process/` → `process_payment()` - Process payment (AJAX)
- `/payment/webhook/` → `stripe_webhook()` - Stripe webhook

### Promo Codes (api.py)
- `/promo/apply/` → `apply_promo_code()` - Apply code (AJAX POST)
- `/promo/remove/` → `remove_promo_code()` - Remove code (AJAX POST)

### Reviews (api.py)
- `/product/<cat>/<prod>/review/` → `submit_review()` - Submit review (AJAX POST)

### Quotes (quote.py)
- `/quote/` → `quote_request()` - Quote form (handles GET/POST)

### Error Handling (api.py)
- Rate limit errors → `ratelimit_error()` - 429 Too Many Requests

## By Size
1. **cart.py** (355 lines) - Most complex, lots of AJAX logic
2. **checkout.py** (330 lines) - Checkout process, email functions
3. **home.py** (192 lines) - Static pages, contact form
4. **catalog.py** (200 lines) - Product display logic
5. **payment.py** (210 lines) - Stripe integration
6. **api.py** (138 lines) - AJAX endpoints
7. **industry.py** (58 lines) - Dynamic industry pages
8. **quote.py** (56 lines) - Quote submission
9. **utils.py** (75 lines) - Shared utilities

## By Feature
| Feature | Module | Views |
|---------|--------|-------|
| Browsing | home.py, catalog.py, industry.py | 17 views |
| Cart | cart.py | 9 views |
| Checkout | checkout.py | 3 views |
| Payment | payment.py | 3 views |
| API/AJAX | api.py | 4 views |
| Forms | quote.py, home.py | 2 views |

## Importing Views

### From Package (Recommended)
```python
from core.views import checkout, product_detail, add_to_cart
```

### From Specific Module
```python
from core.views.checkout import checkout
from core.views.catalog import product_detail
from core.views.cart import add_to_cart
```

### In URLs (No Change!)
```python
from . import views
urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    # ... all patterns work as before
]
```

## Common Patterns

### Handling AJAX Requests
```python
# In cart.py
is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
if is_ajax:
    return JsonResponse({'success': True, 'data': ...})
else:
    return redirect('core:cart')
```

### Using Cart
```python
from .cart import get_or_create_cart
cart = get_or_create_cart(request)
# Access cart.total_items, cart.subtotal, etc.
```

### Calculating Totals
```python
from .utils import calculate_order_totals, build_shipping_methods
shipping_methods = build_shipping_methods(cart)
totals = calculate_order_totals(cart, 'standard', 'ON')
# totals has: shipping_cost, tax_amount, grand_total, etc.
```

### Getting Cart for Update
```python
# Most AJAX endpoints need this pattern:
from .cart import get_or_create_cart
cart = get_or_create_cart(request)
# Then interact with cart.items
```

## Migration Checklist

If updating imports:
- [ ] Update `from core.views import ...` statements (optional)
- [ ] Run `manage.py check` to verify
- [ ] Test cart operations
- [ ] Test checkout flow
- [ ] Test AJAX endpoints
- [ ] Verify email sending

## Debugging Tips

### Lost in code?
1. Check the module map above
2. Search for view name in that module
3. Use module docstring for context

### Circuit issue in cart?
- Check `cart.py` - handles all cart operations
- Check `get_or_create_cart()` - helper at top of file

### Checkout broken?
- Start in `checkout.py` 
- Check utils for `calculate_order_totals()`
- Check `payment.py` for Stripe integration

### AJAX not working?
- Search in `api.py` or `cart.py`
- Look for `@require_POST` decorator
- Check `X-Requested-With` header handling

### Email not sending?
- Check `send_order_confirmation_email()` in `checkout.py`
- Check `send_order_notification_email()` in `checkout.py`
- Verify settings.py EMAIL configuration

## Adding New Views

### To existing module:
1. Open the appropriate module (e.g., `catalog.py`)
2. Add your view function
3. Update `__init__.py` if not already imported
4. Add URL pattern to `core/urls.py`

### New feature in new module:
1. Create `views/myfeature.py`
2. Add views to that file
3. Import in `views/__init__.py`
4. Add URL pattern to `core/urls.py`

Example: `views/reviews.py`
```python
# core/views/reviews.py
def review_list(request):
    reviews = ProductReview.objects.filter(is_approved=True)
    return render(request, 'reviews/list.html', {'reviews': reviews})

# Then in __init__.py:
from .reviews import review_list
```

## Performance Notes

- **cart.py**: Uses `select_related('product')` and `prefetch_related()` for performance
- **checkout.py**: Uses database transactions for consistency
- **payment.py**: Uses Stripe idempotency keys to prevent duplicates
- **api.py**: Most AJAX endpoints return lightweight JsonResponse
- **home.py**: Uses caching for menu items and product categories

---

**Last Updated:** January 2, 2026  
**Phase:** 3 (Views Refactoring)  
**Status:** ✅ Complete and Deployed
