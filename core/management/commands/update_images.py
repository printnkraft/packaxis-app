from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = 'Update product images to use media folder paths'

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating product images...')
        
        products = {
            'shopping-paper-bags': 'products/Shopping Paper Bags.jpg',
            'brown-kraft-bags': 'products/Brown Kraft Bag.jpg',
            'white-paper-bags': 'products/White Paper Bag.jpg',
            'custom-branded-bags': 'products/Custom Paper Bag.jpg',
            'paper-straws': 'products/Paper Straw.jpg',
        }
        
        for slug, image_path in products.items():
            try:
                product = Product.objects.get(slug=slug)
                product.image = image_path
                product.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Updated {product.title}'))
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'✗ Product {slug} not found'))
        
        self.stdout.write(self.style.SUCCESS('✅ Product images updated!'))
