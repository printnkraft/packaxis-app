from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products_page, name='products'),
    path('services/', views.services_page, name='services'),
    path('industries/', views.industries_page, name='industries'),
    path('contact/', views.contact_page, name='contact'),
    path('pricing-brochure/', views.pricing_brochure, name='pricing_brochure'),
    path('faq/', views.faq, name='faq'),
    path('quote/', views.quote_request, name='quote_request'),
    path('product/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    
    # Industry-Specific Landing Pages
    path('restaurant-paper-bags/', views.restaurant_paper_bags, name='restaurant_paper_bags'),
    path('retail-paper-bags/', views.retail_paper_bags, name='retail_paper_bags'),
    path('boutique-packaging/', views.boutique_packaging, name='boutique_packaging'),
    path('grocery-paper-bags/', views.grocery_paper_bags, name='grocery_paper_bags'),
    path('bakery-paper-bags/', views.bakery_paper_bags, name='bakery_paper_bags'),
    
    # E-commerce / Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update-ajax/<int:item_id>/', views.update_cart_ajax, name='update_cart_ajax'),
    path('cart/set-quantity-ajax/<int:item_id>/', views.set_cart_quantity_ajax, name='set_cart_quantity_ajax'),
    path('cart/remove-ajax/<int:item_id>/', views.remove_cart_ajax, name='remove_cart_ajax'),
    path('cart/dropdown-html/', views.cart_dropdown_html, name='cart_dropdown_html'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('invoice/<str:order_number>/', views.download_invoice, name='download_invoice'),
    
    # Promo Code URLs
    path('promo/apply/', views.apply_promo_code, name='apply_promo_code'),
    path('promo/remove/', views.remove_promo_code, name='remove_promo_code'),
    
    # Stripe Payment URLs
    path('payment/create-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
