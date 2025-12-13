from django.db import models

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


class Product(models.Model):
    """Products displayed on the homepage"""
    title = models.CharField(max_length=200, help_text="Product title")
    description = models.TextField(help_text="Product description")
    image = models.ImageField(upload_to='products/', help_text="Product image")
    slug = models.SlugField(unique=True, help_text="URL-friendly version of title (auto-generated)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this product")
    category = models.CharField(max_length=100, blank=True, help_text="Product category")
    
    # Product details for detail page
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
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
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
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, help_text="Product of interest")
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
        return f"Quote from {self.name} - {self.product.title if self.product else 'No Product'}"


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
