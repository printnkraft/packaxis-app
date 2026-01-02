"""
Industry-specific page views.
Includes: dynamic industry detail pages, legacy industry landing pages.
"""
from django.shortcuts import render
from django.http import Http404
from django.db import models
from ..models import Industry, Product


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
        'is_industry': True,  # Flag to show different breadcrumbs in template
    }
    return render(request, 'core/category-detail.html', context)


# ============================================
# LEGACY INDUSTRY-SPECIFIC LANDING PAGES
# ============================================

def restaurant_paper_bags(request):
    """Legacy restaurant industry landing page"""
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
