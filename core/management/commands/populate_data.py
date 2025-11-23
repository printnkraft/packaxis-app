from django.core.management.base import BaseCommand
from core.models import MenuItem, Product, Service
from django.core.files import File
from pathlib import Path
import os

class Command(BaseCommand):
    help = 'Populate database with initial data from static site'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating menu items...')
        
        # Create top-level menu items
        products_menu = MenuItem.objects.create(
            title='Products',
            url='#products',
            order=2,
            is_active=True
        )
        
        MenuItem.objects.create(
            title='Services',
            url='#services',
            order=3,
            is_active=True
        )
        
        MenuItem.objects.create(
            title='About',
            url='#about',
            order=4,
            is_active=True
        )
        
        MenuItem.objects.create(
            title='Contact',
            url='#contact',
            order=5,
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Menu items created'))
        
        # Create products
        self.stdout.write('Creating products...')
        
        Product.objects.create(
            title='Shopping Paper Bags',
            slug='shopping-paper-bags',
            category='Retail Packaging',
            description='Premium kraft paper bags perfect for retail stores, boutiques, and shopping centers. Durable, eco-friendly, and customizable to match your brand.',
            order=1,
            is_active=True,
            material='Premium Kraft Paper',
            gsm_range='100-300 GSM',
            handle_type='Twisted/Flat Paper Handles',
            customization='Multiple sizes available',
            feature_1='Customizable with your logo and branding',
            feature_2='100% Recyclable and biodegradable',
            feature_3='Strong reinforced handles',
            feature_4='Ideal for retail and shopping',
            feature_5='Available in bulk quantities',
            feature_6='Fast turnaround time'
        )
        
        Product.objects.create(
            title='Brown Kraft Bags',
            slug='brown-kraft-bags',
            category='Grocery & Food Packaging',
            description='Classic eco-friendly brown kraft bags for groceries, food service, and general retail use. Strong, reliable, and environmentally responsible.',
            order=2,
            is_active=True,
            material='Natural Brown Kraft Paper',
            gsm_range='80-250 GSM',
            handle_type='Flat Paper Handles',
            customization='FDA Approved - Food Safe',
            feature_1='Food-safe and hygienic',
            feature_2='Natural unbleached paper',
            feature_3='Eco-friendly and sustainable',
            feature_4='Perfect for groceries and food',
            feature_5='Cost-effective bulk pricing',
            feature_6='Custom printing available'
        )
        
        Product.objects.create(
            title='White Paper Bags',
            slug='white-paper-bags',
            category='Premium Retail Packaging',
            description='Professional white paper bags perfect for bakeries, boutiques, and high-end retail. Clean, elegant, and ideal for brand customization.',
            order=3,
            is_active=True,
            material='Bleached White Kraft Paper',
            gsm_range='100-300 GSM',
            handle_type='Flat/Twisted Paper Handles',
            customization='Smooth White Finish',
            feature_1='Premium white appearance',
            feature_2='Perfect for bakeries and cafes',
            feature_3='Excellent print quality for logos',
            feature_4='Food-grade certified',
            feature_5='Professional and elegant',
            feature_6='Multiple size options'
        )
        
        Product.objects.create(
            title='Custom Branded Bags',
            slug='custom-branded-bags',
            category='Luxury Custom Packaging',
            description='Fully customizable premium paper bags with your brand logo, colors, and designs. Perfect for events, luxury retail, and brand promotions.',
            order=4,
            is_active=True,
            material='Choice of Kraft or Coated Paper',
            gsm_range='Full Color CMYK Printing',
            handle_type='Rope, Ribbon, or Paper Handles',
            customization='Complete Design Freedom',
            feature_1='Full custom design and branding',
            feature_2='High-quality printing',
            feature_3='Premium materials available',
            feature_4='Perfect for events and gifting',
            feature_5='Low minimum order quantities',
            feature_6='Professional design support'
        )
        
        Product.objects.create(
            title='Paper Straws',
            slug='paper-straws',
            category='Eco-Friendly Accessories',
            description='Sustainable paper straws as an eco-friendly alternative to plastic. Perfect for restaurants, cafes, and events.',
            order=5,
            is_active=True,
            material='Food-Grade Paper',
            gsm_range='197mm (7.75 inches) Length',
            handle_type='6mm Standard Diameter',
            customization='Plain or Striped Colors',
            feature_1='100% biodegradable',
            feature_2='FDA approved food-safe',
            feature_3='Durable in liquids',
            feature_4='Plain and striped options',
            feature_5='Bulk pricing available',
            feature_6='Perfect for eco-conscious businesses'
        )
        
        # Create dropdown menu items for products
        MenuItem.objects.create(
            title='Shopping Paper Bags',
            parent=products_menu,
            url='/product/shopping-paper-bags/',
            order=1,
            is_active=True
        )
        
        MenuItem.objects.create(
            title='Brown Kraft Bags',
            parent=products_menu,
            url='/product/brown-kraft-bags/',
            order=2,
            is_active=True
        )
        
        MenuItem.objects.create(
            title='White Paper Bags',
            parent=products_menu,
            url='/product/white-paper-bags/',
            order=3,
            is_active=True
        )
        
        MenuItem.objects.create(
            title='Custom Branded Bags',
            parent=products_menu,
            url='/product/custom-branded-bags/',
            order=4,
            is_active=True
        )
        
        MenuItem.objects.create(
            title='Paper Straws',
            parent=products_menu,
            url='/product/paper-straws/',
            order=5,
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Products created'))
        
        # Create services
        self.stdout.write('Creating services...')
        
        Service.objects.create(
            title='Customized Packaging Solutions',
            description='Tailored paper bags with your brand logo, colors, and unique designs. From concept to delivery, we bring your vision to life.',
            icon='📦',
            order=1,
            is_active=True
        )
        
        Service.objects.create(
            title='Outstanding Customer Support',
            description='Dedicated team ready to assist with product selection, customization, and order tracking. We\'re here for you every step of the way.',
            icon='🤝',
            order=2,
            is_active=True
        )
        
        Service.objects.create(
            title='Visual Copy of Packaging',
            description='Get digital mockups and samples before production. See exactly how your custom bags will look before placing bulk orders.',
            icon='🖥️',
            order=3,
            is_active=True
        )
        
        Service.objects.create(
            title='Quality Packaging Solutions',
            description='Premium kraft, bleached, coated and uncoated papers. Every bag undergoes strict quality control for durability and excellence.',
            icon='⭐',
            order=4,
            is_active=True
        )
        
        Service.objects.create(
            title='Timely Delivery',
            description='Fast turnaround times and reliable Canada-wide shipping. Get your bulk orders delivered on time, every time.',
            icon='🚚',
            order=5,
            is_active=True
        )
        
        Service.objects.create(
            title='Eco-Friendly Materials',
            description='100% recyclable and biodegradable paper bags. Help your business go green with sustainable packaging options.',
            icon='🌱',
            order=6,
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Services created'))
        self.stdout.write(self.style.SUCCESS('✅ All data populated successfully!'))
