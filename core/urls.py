from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products_page, name='products'),
    path('services/', views.services_page, name='services'),
    path('industries/', views.industries_page, name='industries'),
    path('pricing-brochure/', views.pricing_brochure, name='pricing_brochure'),
    path('faq/', views.faq, name='faq'),
    path('quote/', views.quote_request, name='quote_request'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    
    # Industry-Specific Landing Pages
    path('restaurant-paper-bags/', views.restaurant_paper_bags, name='restaurant_paper_bags'),
    path('retail-paper-bags/', views.retail_paper_bags, name='retail_paper_bags'),
    path('boutique-packaging/', views.boutique_packaging, name='boutique_packaging'),
    path('grocery-paper-bags/', views.grocery_paper_bags, name='grocery_paper_bags'),
    path('bakery-paper-bags/', views.bakery_paper_bags, name='bakery_paper_bags'),
]
