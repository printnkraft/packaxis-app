"""
Product catalog views.
Includes: product detail, category detail, legacy product landing pages.
"""
from django.shortcuts import render, get_object_or_404
from ..models import Product, ProductCategory


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


# ============================================
# LEGACY PRODUCT LANDING PAGES
# ============================================
# These are static context views for classic product pages
# They now pass context to the same template

def brown_kraft_bags(request):
    """Brown Kraft Bags product page"""
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
    """White Paper Bags product page"""
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
    """Custom Branded Bags product page"""
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
    """Paper Straws product page"""
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
