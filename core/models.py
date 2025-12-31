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
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]
    
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
    
    # Additional features (expanded to 6)
    feature_1 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_2 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_3 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_4 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_5 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    feature_6 = models.CharField(max_length=200, blank=True, help_text="Product feature")
    
    # SEO & Metadata
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO title (max 70 chars)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (max 160 chars)")
    canonical_url = models.URLField(blank=True, help_text="Canonical URL if different from default")
    search_keywords = models.TextField(blank=True, help_text="Internal search keywords (comma-separated)")
    schema_type = models.CharField(max_length=50, default='Product', help_text="Schema.org type")
    
    # Industries (many-to-many through ProductIndustry)
    industries = models.ManyToManyField('Industry', through='ProductIndustry', blank=True, 
                                         related_name='products_direct', help_text="Industries this product serves")
    
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
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['sku']),
            models.Index(fields=['created_at']),
        ]
    
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
    
    @property
    def average_rating(self):
        """Calculate average rating from approved reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0
    
    @property
    def review_count(self):
        """Count approved reviews"""
        return self.reviews.filter(is_approved=True).count()
    
    def get_tiered_price(self, quantity):
        """Get price for a specific quantity based on tiered pricing"""
        tiered = self.tiered_prices.filter(
            min_quantity__lte=quantity
        ).filter(
            models.Q(max_quantity__gte=quantity) | models.Q(max_quantity__isnull=True)
        ).first()
        if tiered:
            return tiered.price_per_unit
        return self.price
    
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
        for i in range(1, 7):  # Now supports 6 features
            feature = getattr(self, f'feature_{i}', '')
            if feature:
                features.append(feature)
        return features
    
    def get_size_variants(self):
        """Get size variants for this product"""
        return self.variants.filter(variant_type='size', is_active=True).order_by('order')
    
    def get_color_variants(self):
        """Get color variants for this product"""
        return self.variants.filter(variant_type='color', is_active=True).order_by('order')
    
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
    
    # Tax rates for Canada
    TAX_RATES = {
        'ON': Decimal('0.13'),  # Ontario HST
        'BC': Decimal('0.12'),  # BC PST + GST
        'AB': Decimal('0.05'),  # Alberta GST only
        'QC': Decimal('0.14975'),  # Quebec GST + QST
        'MB': Decimal('0.12'),  # Manitoba PST + GST
        'SK': Decimal('0.11'),  # Saskatchewan PST + GST
        'NS': Decimal('0.15'),  # Nova Scotia HST
        'NB': Decimal('0.15'),  # New Brunswick HST
        'NL': Decimal('0.15'),  # Newfoundland HST
        'PE': Decimal('0.15'),  # PEI HST
        'NT': Decimal('0.05'),  # GST only
        'YT': Decimal('0.05'),  # GST only
        'NU': Decimal('0.05'),  # GST only
    }
    
    FREE_SHIPPING_THRESHOLD = Decimal('2000.00')
    
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
        """Subtotal of all items in cart (with tiered pricing)"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def original_subtotal(self):
        """What the cart would cost without tiered pricing"""
        return sum(item.original_total for item in self.items.all())
    
    @property
    def total_savings(self):
        """Total savings from tiered pricing"""
        return sum(item.total_savings for item in self.items.all())
    
    @property
    def has_savings(self):
        """Check if cart has any savings"""
        return self.total_savings > 0
    
    @property
    def savings_percentage(self):
        """Overall percentage savings"""
        if self.original_subtotal and self.original_subtotal > 0:
            return int((self.total_savings / self.original_subtotal) * 100)
        return 0
    
    def get_estimated_tax(self, province='ON'):
        """Estimate tax based on province"""
        rate = self.TAX_RATES.get(province.upper(), Decimal('0.13'))
        return (self.subtotal * rate).quantize(Decimal('0.01'))
    
    def get_shipping_estimate(self):
        """Estimate shipping cost"""
        if self.subtotal >= self.FREE_SHIPPING_THRESHOLD:
            return Decimal('0.00')
        # Flat rate shipping for orders under threshold
        if self.subtotal >= Decimal('500.00'):
            return Decimal('29.99')
        elif self.subtotal >= Decimal('200.00'):
            return Decimal('49.99')
        else:
            return Decimal('79.99')
    
    @property
    def shipping_progress(self):
        """Progress towards free shipping (percentage)"""
        if self.subtotal >= self.FREE_SHIPPING_THRESHOLD:
            return 100
        return int((self.subtotal / self.FREE_SHIPPING_THRESHOLD) * 100)
    
    @property
    def amount_to_free_shipping(self):
        """Amount needed for free shipping"""
        remaining = self.FREE_SHIPPING_THRESHOLD - self.subtotal
        return max(Decimal('0.00'), remaining)
    
    def get_total_with_tax(self, province='ON'):
        """Total including tax"""
        return self.subtotal + self.get_estimated_tax(province) + self.get_shipping_estimate()
    
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
    def base_price(self):
        """Get base product price without tiered discount"""
        return self.product.price or Decimal('0.00')
    
    @property
    def unit_price(self):
        """Get tiered unit price based on quantity"""
        base = self.product.price or Decimal('0.00')
        if not base:
            return Decimal('0.00')
        
        # Check for tiered pricing
        tiered_prices = self.product.tiered_prices.filter(
            min_quantity__lte=self.quantity
        ).order_by('-min_quantity').first()
        
        if tiered_prices:
            # Check max_quantity if set
            if tiered_prices.max_quantity is None or self.quantity <= tiered_prices.max_quantity:
                return tiered_prices.price_per_unit
        
        return base
    
    @property
    def applied_tier(self):
        """Get the applied tiered pricing tier"""
        tiered_prices = self.product.tiered_prices.filter(
            min_quantity__lte=self.quantity
        ).order_by('-min_quantity').first()
        
        if tiered_prices:
            if tiered_prices.max_quantity is None or self.quantity <= tiered_prices.max_quantity:
                return tiered_prices
        return None
    
    @property
    def savings_per_unit(self):
        """Calculate savings per unit compared to base price"""
        return max(Decimal('0.00'), self.base_price - self.unit_price)
    
    @property
    def total_savings(self):
        """Total savings on this item"""
        return self.savings_per_unit * self.quantity
    
    @property
    def savings_percentage(self):
        """Percentage savings compared to base price"""
        if self.base_price and self.base_price > 0:
            return int((self.savings_per_unit / self.base_price) * 100)
        return 0
    
    @property
    def total_price(self):
        """Total price for this cart item (with tiered pricing)"""
        return self.unit_price * self.quantity
    
    @property
    def original_total(self):
        """Total price without tiered discount"""
        return self.base_price * self.quantity


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
    
    # Tracking steps for customer view (1-4)
    TRACKING_STEPS = [
        (1, 'Order Placed'),
        (2, 'Processing'),
        (3, 'Shipped'),
        (4, 'Delivered'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Link to User Account (optional - for guest checkout)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders',
        help_text="User account (if logged in during checkout)"
    )
    
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
    
    # Shipping method selection
    shipping_method = models.CharField(max_length=50, blank=True, help_text="Selected shipping method")
    shipping_eta = models.CharField(max_length=100, blank=True, help_text="Estimated delivery window")

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
    promo_code = models.CharField(max_length=50, blank=True, help_text="Applied promo code")
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
    tracking_step = models.IntegerField(default=1, choices=[(1, 'Order Placed'), (2, 'Processing'), (3, 'Shipped'), (4, 'Delivered')], help_text="Current tracking step (1-4)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
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
    
    @property
    def tracking_step_label(self):
        """Get the current tracking step label"""
        step_labels = {1: 'Order Placed', 2: 'Processing', 3: 'Shipped', 4: 'Delivered'}
        return step_labels.get(self.tracking_step, 'Order Placed')
    
    @property 
    def tracking_steps_data(self):
        """Return tracking steps with completion status for template"""
        steps = [
            {'step': 1, 'label': 'Order Placed', 'completed': self.tracking_step >= 1, 'active': self.tracking_step == 1},
            {'step': 2, 'label': 'Processing', 'completed': self.tracking_step >= 2, 'active': self.tracking_step == 2},
            {'step': 3, 'label': 'Shipped', 'completed': self.tracking_step >= 3, 'active': self.tracking_step == 3},
            {'step': 4, 'label': 'Delivered', 'completed': self.tracking_step >= 4, 'active': self.tracking_step == 4},
        ]
        return steps


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


# ============================================
# PRODUCT VARIANTS & PRICING
# ============================================

class ProductVariant(models.Model):
    """Product variants for size, color combinations"""
    VARIANT_TYPES = [
        ('size', 'Size'),
        ('color', 'Color'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_type = models.CharField(max_length=20, choices=VARIANT_TYPES)
    name = models.CharField(max_length=100, help_text="e.g., 'Small', 'Red', '10x12x5'")
    value = models.CharField(max_length=100, help_text="Display value")
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), 
                                           help_text="Price adjustment (+/-) from base price")
    sku_suffix = models.CharField(max_length=50, blank=True, help_text="SKU suffix for this variant")
    stock_quantity = models.IntegerField(default=0, help_text="Stock for this variant")
    image = models.ImageField(upload_to='product-variants/', blank=True, null=True, 
                              help_text="Variant-specific image (optional)")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['product', 'variant_type', 'order']
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
    
    def __str__(self):
        return f"{self.product.title} - {self.get_variant_type_display()}: {self.name}"
    
    @property
    def full_sku(self):
        if self.sku_suffix and self.product.sku:
            return f"{self.product.sku}-{self.sku_suffix}"
        return self.product.sku or ""


class TieredPricing(models.Model):
    """Volume-based tiered pricing for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tiered_prices')
    min_quantity = models.IntegerField(help_text="Minimum quantity for this tier")
    max_quantity = models.IntegerField(null=True, blank=True, help_text="Maximum quantity (leave blank for unlimited)")
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    label = models.CharField(max_length=50, blank=True, help_text="e.g., 'Bulk', 'Wholesale'")
    
    class Meta:
        ordering = ['product', 'min_quantity']
        verbose_name = "Tiered Pricing"
        verbose_name_plural = "Tiered Pricing"
    
    def __str__(self):
        if self.max_quantity:
            return f"{self.product.title}: {self.min_quantity}-{self.max_quantity} units @ ${self.price_per_unit}"
        return f"{self.product.title}: {self.min_quantity}+ units @ ${self.price_per_unit}"
    
    @property
    def quantity_range(self):
        if self.max_quantity:
            return f"{self.min_quantity}–{self.max_quantity}"
        return f"{self.min_quantity}+"


class DiscountRule(models.Model):
    """Discount rules for products"""
    DISCOUNT_TYPES = [
        ('volume', 'Volume Discount'),
        ('customer_group', 'Customer Group'),
        ('promo_code', 'Promo Code'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discount_rules', 
                                null=True, blank=True, help_text="Leave blank for store-wide discount")
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    promo_code = models.CharField(max_length=50, blank=True, help_text="Required for promo code type")
    min_quantity = models.IntegerField(null=True, blank=True, help_text="Minimum quantity for volume discount")
    customer_group = models.CharField(max_length=100, blank=True, help_text="e.g., 'wholesale', 'vip'")
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['product', 'discount_type']
        verbose_name = "Discount Rule"
        verbose_name_plural = "Discount Rules"
    
    def __str__(self):
        return f"{self.name} ({self.get_discount_type_display()})"


# ============================================
# PRODUCT REVIEWS
# ============================================

class ProductReview(models.Model):
    """Customer reviews for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    title = models.CharField(max_length=200, blank=True)
    review = models.TextField()
    image = models.ImageField(upload_to='review-images/', blank=True, null=True, 
                              help_text="Optional review image")
    is_verified = models.BooleanField(default=False, help_text="Verified purchase")
    is_approved = models.BooleanField(default=False, help_text="Approved to display")
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
    
    def __str__(self):
        return f"{self.name} - {self.product.title} ({self.rating}★)"


# ============================================
# PRODUCT-INDUSTRY & PRODUCT-CATEGORY RELATIONS
# ============================================

class ProductIndustry(models.Model):
    """Many-to-many relationship between products and industries"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_industries')
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='industry_products')
    
    class Meta:
        unique_together = ['product', 'industry']
        verbose_name = "Product Industry"
        verbose_name_plural = "Product Industries"
    
    def __str__(self):
        return f"{self.product.title} - {self.industry.title}"


# ============================================
# SITE SETTINGS
# ============================================

class PromoCode(models.Model):
    """Promotional discount codes for checkout"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage Off'),
        ('fixed', 'Fixed Amount Off'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    code = models.CharField(max_length=50, unique=True, help_text="Unique promo code (will be stored uppercase)")
    description = models.CharField(max_length=255, blank=True, help_text="Internal description")
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Percentage or fixed amount")
    
    # Limits
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum order subtotal required")
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cap on discount amount (for percentage codes)")
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Total times this code can be used (blank = unlimited)")
    usage_count = models.PositiveIntegerField(default=0, help_text="Times this code has been used")
    per_user_limit = models.PositiveIntegerField(default=1, help_text="Times each user/email can use this code")
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True, help_text="Start date (blank = immediately)")
    valid_until = models.DateTimeField(null=True, blank=True, help_text="End date (blank = never expires)")
    
    # Restrictions
    first_order_only = models.BooleanField(default=False, help_text="Only valid for first-time customers")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"
    
    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)
    
    def is_valid(self, subtotal, email=None):
        """Check if promo code is valid for given order"""
        from django.utils import timezone
        now = timezone.now()
        
        # Check if active
        if not self.is_active:
            return False, "This promo code is no longer active."
        
        # Check date validity
        if self.valid_from and now < self.valid_from:
            return False, "This promo code is not yet active."
        
        if self.valid_until and now > self.valid_until:
            return False, "This promo code has expired."
        
        # Check usage limit
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, "This promo code has reached its usage limit."
        
        # Check minimum order
        if subtotal < self.minimum_order_amount:
            return False, f"Minimum order of ${self.minimum_order_amount} required for this code."
        
        # Check per-user limit
        if email and self.per_user_limit:
            from core.models import Order
            user_usage = Order.objects.filter(email__iexact=email, promo_code=self.code).count()
            if user_usage >= self.per_user_limit:
                return False, "You've already used this promo code."
        
        # Check first order only
        if self.first_order_only and email:
            from core.models import Order
            if Order.objects.filter(email__iexact=email).exists():
                return False, "This promo code is only valid for first-time customers."
        
        return True, "Valid"
    
    def calculate_discount(self, subtotal, shipping_cost=Decimal('0.00')):
        """Calculate the discount amount"""
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / Decimal('100')
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
            return discount
        elif self.discount_type == 'fixed':
            return min(self.discount_value, subtotal)  # Can't discount more than subtotal
        elif self.discount_type == 'free_shipping':
            return shipping_cost
        return Decimal('0.00')


class SiteSettings(models.Model):
    """Global site settings - only one instance should exist"""
    
    # Payment Settings
    online_payments_enabled = models.BooleanField(
        default=False, 
        help_text="Enable/disable Stripe online payments. When disabled, orders will be placed without payment."
    )
    
    # Store Info
    store_name = models.CharField(max_length=100, default="PackAxis Packaging Canada")
    store_email = models.EmailField(default="hello@packaxis.ca")
    store_phone = models.CharField(max_length=20, default="(647) 555-0123")
    store_address = models.TextField(default="Toronto, Ontario, Canada", blank=True)
    
    # Tax Settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=13.00, help_text="Tax rate percentage (e.g., 13 for 13% HST)")
    
    # Order Settings
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum order amount (0 = no minimum)")
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=500, help_text="Order amount for free shipping")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the singleton settings instance, creating it if needed"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
