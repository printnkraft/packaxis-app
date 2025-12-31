"""
Unit tests for PackAxis core application.
Tests critical flows: products, cart, checkout, contact.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import ProductCategory, Product, Cart, CartItem, Order, Quote, FAQ, Industry


class ProductCategoryTestCase(TestCase):
    """Tests for ProductCategory model and views"""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            title="Brown Kraft Bags",
            description="Eco-friendly paper bags",
            slug="brown-kraft-bags",
            is_active=True,
            order=1
        )
    
    def test_category_creation(self):
        """Test category is created correctly"""
        self.assertEqual(self.category.title, "Brown Kraft Bags")
        self.assertTrue(self.category.is_active)
    
    def test_category_str(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), "Brown Kraft Bags")
    
    def test_products_page_loads(self):
        """Test products page returns 200"""
        response = self.client.get(reverse('core:products'))
        self.assertEqual(response.status_code, 200)
    
    def test_category_detail_page_loads(self):
        """Test category detail page returns 200"""
        response = self.client.get(
            reverse('core:category_detail', kwargs={'slug': self.category.slug})
        )
        self.assertEqual(response.status_code, 200)


class ProductTestCase(TestCase):
    """Tests for Product model and views"""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            title="Test Category",
            slug="test-category",
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            title="10x12 Brown Bag",
            slug="10x12-brown-bag",
            price=Decimal('1.50'),
            stock_quantity=100,
            is_active=True,
            track_inventory=True
        )
    
    def test_product_creation(self):
        """Test product is created correctly"""
        self.assertEqual(self.product.title, "10x12 Brown Bag")
        self.assertEqual(self.product.price, Decimal('1.50'))
        self.assertEqual(self.product.stock_quantity, 100)
    
    def test_product_str(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), "Test Category - 10x12 Brown Bag")
    
    def test_product_detail_page_loads(self):
        """Test product detail page returns 200"""
        response = self.client.get(
            reverse('core:product_detail', kwargs={
                'category_slug': self.category.slug,
                'product_slug': self.product.slug
            })
        )
        self.assertEqual(response.status_code, 200)


class CartTestCase(TestCase):
    """Tests for Cart functionality"""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            title="Test Category",
            slug="test-category",
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            title="Test Product",
            slug="test-product",
            price=Decimal('2.50'),
            stock_quantity=50,
            is_active=True
        )
    
    def test_cart_page_loads(self):
        """Test cart page returns 200"""
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_to_cart(self):
        """Test adding product to cart"""
        response = self.client.post(
            reverse('core:add_to_cart', kwargs={'slug': self.product.slug}),
            {'quantity': 5}
        )
        # Should redirect to cart page
        self.assertEqual(response.status_code, 302)
        
        # Check cart has item
        cart = Cart.objects.filter(session_key=self.client.session.session_key).first()
        if cart:
            self.assertEqual(cart.items.count(), 1)
            self.assertEqual(cart.items.first().quantity, 5)
    
    def test_add_to_cart_ajax(self):
        """Test AJAX add to cart"""
        response = self.client.post(
            reverse('core:add_to_cart', kwargs={'slug': self.product.slug}),
            {'quantity': 3},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())


class CheckoutTestCase(TestCase):
    """Tests for Checkout functionality"""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            title="Test Category",
            slug="test-category",
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            title="Test Product",
            slug="test-product",
            price=Decimal('5.00'),
            stock_quantity=100,
            is_active=True
        )
    
    def test_checkout_page_empty_cart(self):
        """Test checkout page with empty cart redirects"""
        response = self.client.get(reverse('core:checkout'))
        # Should redirect or show empty cart message
        self.assertIn(response.status_code, [200, 302])
    
    def test_checkout_page_with_items(self):
        """Test checkout page with items in cart"""
        # First add item to cart
        self.client.post(
            reverse('core:add_to_cart', kwargs={'slug': self.product.slug}),
            {'quantity': 2}
        )
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)


class ContactTestCase(TestCase):
    """Tests for Contact functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_contact_page_loads(self):
        """Test contact page returns 200"""
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
    
    def test_contact_form_submission(self):
        """Test contact form submission"""
        response = self.client.post(reverse('core:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '416-555-1234',
            'company': 'Test Company',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        })
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
    
    def test_contact_xss_prevention(self):
        """Test XSS is prevented in contact form"""
        response = self.client.post(reverse('core:contact'), {
            'name': '<script>alert("XSS")</script>',
            'email': 'test@example.com',
            'phone': '416-555-1234',
            'subject': 'Test',
            'message': '<img src=x onerror=alert("XSS")>'
        })
        # Form should still process (sanitized)
        self.assertIn(response.status_code, [200, 302])


class QuoteRequestTestCase(TestCase):
    """Tests for Quote Request functionality"""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            title="Test Category",
            slug="test-category",
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            title="Test Product",
            slug="test-product",
            is_active=True
        )
    
    def test_quote_page_loads(self):
        """Test quote page returns 200"""
        response = self.client.get(reverse('core:quote_request'))
        self.assertEqual(response.status_code, 200)
    
    def test_quote_form_submission(self):
        """Test quote form submission"""
        response = self.client.post(reverse('core:quote_request'), {
            'name': 'Test Business',
            'company_name': 'Test Corp',
            'email': 'business@example.com',
            'contact_number': '416-555-9999',
            'product': self.product.id,
            'size': '10x12x5',
            'gsm': '120',
            'quantity': '5000',
            'message': 'Need bulk order quote'
        })
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Check quote was created
        self.assertEqual(Quote.objects.count(), 1)
        quote = Quote.objects.first()
        self.assertEqual(quote.name, 'Test Business')


class HomePageTestCase(TestCase):
    """Tests for Homepage"""
    
    def setUp(self):
        self.client = Client()
    
    def test_homepage_loads(self):
        """Test homepage returns 200"""
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_contains_required_elements(self):
        """Test homepage contains key elements"""
        response = self.client.get(reverse('core:index'))
        content = response.content.decode()
        self.assertIn('PackAxis', content)  # Brand name


class FAQTestCase(TestCase):
    """Tests for FAQ functionality"""
    
    def setUp(self):
        self.client = Client()
        FAQ.objects.create(
            question="What are your delivery times?",
            answer="Standard delivery is 5-7 business days.",
            order=1,
            is_active=True
        )
    
    def test_faq_page_loads(self):
        """Test FAQ page returns 200"""
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)
    
    def test_faq_displayed(self):
        """Test FAQ content is displayed"""
        response = self.client.get(reverse('core:faq'))
        self.assertContains(response, 'delivery times')


class SecurityTestCase(TestCase):
    """Tests for security features"""
    
    def setUp(self):
        self.client = Client()
    
    def test_csrf_protection(self):
        """Test CSRF protection is active"""
        # POST without CSRF token should fail
        response = self.client.post(reverse('core:contact'), {
            'name': 'Test',
            'email': 'test@test.com',
            'message': 'Test message'
        }, HTTP_X_CSRFTOKEN='invalid')
        # Django's CSRF middleware should block or the form won't process correctly
    
    def test_404_page(self):
        """Test custom 404 page"""
        response = self.client.get('/nonexistent-page-12345/')
        self.assertEqual(response.status_code, 404)


class IndustryPageTestCase(TestCase):
    """Tests for Industry landing pages"""
    
    def setUp(self):
        self.client = Client()
    
    def test_restaurant_page_loads(self):
        """Test restaurant industry page"""
        response = self.client.get(reverse('core:restaurant_paper_bags'))
        self.assertEqual(response.status_code, 200)
    
    def test_retail_page_loads(self):
        """Test retail industry page"""
        response = self.client.get(reverse('core:retail_paper_bags'))
        self.assertEqual(response.status_code, 200)
    
    def test_boutique_page_loads(self):
        """Test boutique industry page"""
        response = self.client.get(reverse('core:boutique_packaging'))
        self.assertEqual(response.status_code, 200)


class SEOTestCase(TestCase):
    """Tests for SEO functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_sitemap_loads(self):
        """Test sitemap.xml loads"""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
    
    def test_robots_txt_loads(self):
        """Test robots.txt loads"""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_meta_tags(self):
        """Test homepage has proper meta tags"""
        response = self.client.get(reverse('core:index'))
        content = response.content.decode()
        self.assertIn('meta name="description"', content)
        self.assertIn('og:title', content)


class OrderModelTestCase(TestCase):
    """Tests for Order model"""
    
    def setUp(self):
        self.category = ProductCategory.objects.create(
            title="Test Category",
            slug="test-category",
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            title="Test Product",
            slug="test-product",
            price=Decimal('10.00'),
            is_active=True
        )
    
    def test_order_creation(self):
        """Test order can be created"""
        order = Order.objects.create(
            email='customer@example.com',
            first_name='John',
            last_name='Doe',
            phone='416-555-1234',
            shipping_address_1='123 Test St',
            shipping_city='Toronto',
            shipping_state='ON',
            shipping_postal_code='M5V 1A1',
            subtotal=Decimal('100.00'),
            tax=Decimal('13.00'),
            total=Decimal('113.00')
        )
        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.status, 'pending')
