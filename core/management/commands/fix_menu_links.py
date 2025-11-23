from django.core.management.base import BaseCommand
from core.models import MenuItem

class Command(BaseCommand):
    help = 'Fix menu links to work from all pages'

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating menu links...')
        
        # Update Services link
        services = MenuItem.objects.filter(title='Services').first()
        if services:
            services.url = '/#services'
            services.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Updated Services link to {services.url}'))
        
        # Update About link
        about = MenuItem.objects.filter(title='About').first()
        if about:
            about.url = '/#about'
            about.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Updated About link to {about.url}'))
        
        # Update Contact link
        contact = MenuItem.objects.filter(title='Contact').first()
        if contact:
            contact.url = '/#contact'
            contact.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Updated Contact link to {contact.url}'))
        
        # Update Products link
        products = MenuItem.objects.filter(title='Products').first()
        if products:
            products.url = '/#products'
            products.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Updated Products link to {products.url}'))
        
        self.stdout.write(self.style.SUCCESS('\nAll menu links updated successfully!'))
