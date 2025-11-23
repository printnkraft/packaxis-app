from django.shortcuts import render, get_object_or_404
from .models import MenuItem, Product

def index(request):
    products = Product.objects.filter(is_active=True)
    context = {
        'products': products
    }
    return render(request, 'core/index.html', context)

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
