from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid

class MenuItem(models.Model):
    """Navigation menu items with optional dropdown support"""
    title = models.CharField(max_length=100, help_text="Menu item title")
    url = models.CharField(max_length=200, blank=True, help_text="URL path (e.g., /about/ or leave blank for dropdown parent)")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', help_text="Leave blank for top-level menu item")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this menu item")
    open_in_new_tab = models.BooleanField(default=False, help_text="Open link in new tab")
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.title} → {self.title}"
        return self.title
    
    def has_children(self):
        return self.children.filter(is_active=True).exists()


class ProductCategory(models.Model):
    """Product categories displayed on the homepage and products page"""
    title = models.CharField(max_length=200, help_text="Category name (e.g., Brown Kraft Bags)")
    description = models.TextField(blank=True, help_text="Category description (e.g., Grocery & Food Packaging)")
    image = models.ImageField(upload_to='product-categories/', help_text="Category image")
    slug = models.SlugField(unique=True, help_text="URL-friendly version of title (auto-generated)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this category")
    
    # Category details for detail page
    material = models.CharField(max_length=200, blank=True, help_text="e.g., 100% Recyclable Kraft Paper")
    gsm_range = models.CharField(max_length=100, blank=True, help_text="e.g., 100-300 GSM")
    handle_type = models.CharField(max_length=200, blank=True, help_text="e.g., Twisted/Flat handles available")
    customization = models.CharField(max_length=200, blank=True, help_text="e.g., Custom sizes and printing")
    
    feature_1 = models.CharField(max_length=200, blank=True)
    feature_2 = models.CharField(max_length=200, blank=True)
    feature_3 = models.CharField(max_length=200, blank=True)
    feature_4 = models.CharField(max_length=200, blank=True)
    feature_5 = models.CharField(max_length=200, blank=True)
    feature_6 = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
    
    def __str__(self):
        return self.title
    
    def get_specifications(self):
        """Return list of specifications for template"""
        specs = []
        if self.material:
            specs.append({'label': 'Material', 'value': self.material})
        if self.gsm_range:
            specs.append({'label': 'GSM Range', 'value': self.gsm_range})
        if self.handle_type:
            specs.append({'label': 'Handle Type', 'value': self.handle_type})
        if self.customization:
            specs.append({'label': 'Customization', 'value': self.customization})
        return specs
    
    def get_features(self):
        """Return list of non-empty features"""
        features = []
        for i in range(1, 7):
            feature = getattr(self, f'feature_{i}', '')
            if feature:
                features.append(feature)
        return features


class Product(models.Model):
    """Individual products that belong to a ProductCategory"""
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products', help_text="Product category")
    title = models.CharField(max_length=200, help_text="Product name (e.g., 10x12x5 Brown Kraft Bag)")
    description = models.TextField(blank=True, help_text="Product description (optional)")
    image = models.ImageField(upload_to='products/', help_text="Product image")
    slug = models.SlugField(unique=True, help_text="URL-friendly version of title (auto-generated)")
    
    # E-commerce pricing fields
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price per unit (e.g., 0.65)")
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original price for showing discount")
    price_per = models.CharField(max_length=50, default='piece', help_text="Price per unit type (e.g., piece, bag, case)")
    
    # Inventory
    sku = models.CharField(max_length=100, blank=True, help_text="Stock Keeping Unit")
    stock_quantity = models.IntegerField(default=0, help_text="Available stock quantity")
    track_inventory = models.BooleanField(default=True, help_text="Track inventory for this product")
    allow_backorder = models.BooleanField(default=False, help_text="Allow orders when out of stock")
    
    # Product specifications
    size = models.CharField(max_length=100, blank=True, help_text="e.g., 10x12x5 inches")
    gsm = models.CharField(max_length=50, blank=True, help_text="e.g., 120 GSM")
    color = models.CharField(max_length=100, blank=True, help_text="e.g., Brown, White, Custom")
    handle_type = models.CharField(max_length=200, blank=True, help_text="e.g., Twisted, Flat, No Handle")
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Weight in kg for shipping")
    
    # Legacy field (kept for backward compatibility)
    price_range = models.CharField(max_length=100, blank=True, help_text="e.g., $0.50 - $1.00 per piece")
    minimum_order = models.IntegerField(null=True, blank=True, help_text="Minimum order quantity")
    case_quantity = models.IntegerField(default=1, help_text="Number of pieces per case")
    
    # Additional features
    feature_1 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_2 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_3 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_4 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    
    # Display settings
    order = models.IntegerField(default=0, help_text="Display order within category (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this product")
    is_featured = models.BooleanField(default=False, help_text="Feature on homepage")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category__order', 'order', 'title']
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    def __str__(self):
        return f"{self.category.title} - {self.title}"
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorder
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_at_price exists"""
        if self.compare_at_price and self.price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0
    
    @property
    def display_price(self):
        """Return formatted price for display"""
        if self.price:
            return f"${self.price:.2f}"
        return self.price_range or "Contact for pricing"
    
    def get_specifications(self):
        """Return list of specifications for template"""
        specs = []
        if self.size:
            specs.append({'label': 'Size', 'value': self.size})
        if self.gsm:
            specs.append({'label': 'GSM', 'value': self.gsm})
        if self.color:
            specs.append({'label': 'Color', 'value': self.color})
        if self.handle_type:
            specs.append({'label': 'Handle Type', 'value': self.handle_type})
        if self.price_range:
            specs.append({'label': 'Price Range', 'value': self.price_range})
        if self.minimum_order:
            specs.append({'label': 'Minimum Order', 'value': f"{self.minimum_order} pieces"})
        return specs
    
    def get_features(self):
        """Return list of non-empty features"""
        features = []
        for i in range(1, 5):
            feature = getattr(self, f'feature_{i}', '')
            if feature:
                features.append(feature)
        return features
    
    def get_all_images(self):
        """Return list of all product images including main image"""
        images = []
        # Add main image first
        if self.image:
            images.append({
                'url': self.image.url,
                'alt': self.title,
                'is_main': True
            })
        # Add additional images
        for img in self.additional_images.filter(is_active=True):
            images.append({
                'url': img.image.url,
                'alt': img.alt_text or self.title,
                'is_main': False
            })
        return images


class ProductImage(models.Model):
    """Additional images for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images', help_text="Product this image belongs to")
    image = models.ImageField(upload_to='product-images/', help_text="Product image")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for image (optional)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this image")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['product', 'order', 'id']
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
    
    def __str__(self):
        return f"{self.product.title} - Image {self.order}"


class Service(models.Model):
    """Services displayed on the homepage"""
    title = models.CharField(max_length=200, help_text="Service title")
    description = models.TextField(help_text="Service description")
    icon = models.CharField(max_length=100, help_text="Icon class (e.g., 🎨 or emoji)", default="📦")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this service")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Service"
        verbose_name_plural = "Services"
    
    def __str__(self):
        return self.title


class Industry(models.Model):
    """Industries displayed on the homepage"""
    title = models.CharField(max_length=200, help_text="Industry name (e.g., Restaurant & Takeout)")
    image = models.ImageField(upload_to='industries/', help_text="Industry icon/image")
    url = models.CharField(max_length=200, help_text="URL path (e.g., /restaurant-paper-bags/)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this industry")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Industry"
        verbose_name_plural = "Industries"
    
    def __str__(self):
        return self.title


class Quote(models.Model):
    """Quote requests from customers"""
    name = models.CharField(max_length=200, help_text="Customer name")
    company_name = models.CharField(max_length=200, blank=True, help_text="Company name (optional)")
    email = models.EmailField(help_text="Customer email")
    contact_number = models.CharField(max_length=20, help_text="Contact phone number")
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, help_text="Specific product of interest")
    product_category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, null=True, blank=True, help_text="Product category of interest")
    size = models.CharField(max_length=100, help_text="Required size (e.g., 10x12x5 inches)")
    gsm = models.CharField(max_length=50, help_text="GSM specification (e.g., 120 GSM)")
    quantity = models.IntegerField(help_text="Quantity needed")
    message = models.TextField(blank=True, help_text="Additional requirements or notes")
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, help_text="Mark as processed")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quote Request"
        verbose_name_plural = "Quote Requests"
    
    def __str__(self):
        if self.product:
            return f"Quote from {self.name} - {self.product.title}"
        elif self.product_category:
            return f"Quote from {self.name} - {self.product_category.title}"
        return f"Quote from {self.name} - No Product"


class FAQ(models.Model):
    """Frequently Asked Questions"""
    
    question = models.CharField(max_length=300, help_text="The question")
    answer = models.TextField(help_text="The answer (supports HTML)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional category for grouping FAQs"
    )
    is_active = models.BooleanField(default=True, help_text="Show on FAQ page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question


# ============================================
# E-COMMERCE MODELS
# ============================================

class Cart(models.Model):
    """Shopping cart for users"""
    session_key = models.CharField(max_length=255, unique=True, help_text="Session identifier for guest users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"
    
    def __str__(self):
        return f"Cart {self.id} - {self.session_key[:20]}..."
    
    @property
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Subtotal of all items in cart"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total(self):
        """Total including any fees (can add shipping, tax later)"""
        return self.subtotal


class CartItem(models.Model):
    """Items in a shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title}"
    
    @property
    def unit_price(self):
        """Get product price"""
        return self.product.price or Decimal('0.00')
    
    @property
    def total_price(self):
        """Total price for this cart item"""
        return self.unit_price * self.quantity


class Order(models.Model):
    """Customer orders"""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Customer Information
    email = models.EmailField(help_text="Customer email")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20)
    
    # Shipping Address
    shipping_address_1 = models.CharField(max_length=255)
    shipping_address_2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='Canada')
    
    # Billing Address (same as shipping by default)
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_address_1 = models.CharField(max_length=255, blank=True)
    billing_address_2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Payment info
    payment_method = models.CharField(max_length=50, blank=True, help_text="Payment method used")
    payment_id = models.CharField(max_length=255, blank=True, help_text="Payment provider transaction ID")
    
    # Notes
    customer_notes = models.TextField(blank=True, help_text="Notes from customer")
    admin_notes = models.TextField(blank=True, help_text="Internal notes")
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    tracking_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number: PA-YYYYMMDD-XXXX
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            self.order_number = f"PA-{date_str}-{random_str}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def shipping_address(self):
        """Return formatted shipping address"""
        parts = [self.shipping_address_1]
        if self.shipping_address_2:
            parts.append(self.shipping_address_2)
        parts.append(f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}")
        parts.append(self.shipping_country)
        return '\n'.join(parts)


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=200, help_text="Product title at time of order")
    product_sku = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
    
    def __str__(self):
        return f"{self.quantity}x {self.product_title}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
