from django.contrib import admin
from django.utils.html import format_html
from .models import MenuItem, Product, ProductImage, ProductCategory, Service, Quote, FAQ, Industry

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent', 'url', 'order', 'is_active', 'has_children']
    list_filter = ['is_active', 'parent']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'url']
    prepopulated_fields = {}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'url', 'parent')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active', 'open_in_new_tab')
        }),
    )
    
    def has_children(self, obj):
        return obj.has_children()
    has_children.boolean = True
    has_children.short_description = 'Has Dropdown'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'description', 'product_count', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'image'),
            'description': 'Core category information displayed on the website'
        }),
        ('Category Specifications', {
            'fields': ('material', 'gsm_range', 'handle_type', 'customization'),
            'description': 'Technical specifications shown on category detail page',
            'classes': ('collapse',)
        }),
        ('Category Features', {
            'fields': ('feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5', 'feature_6'),
            'description': 'Add up to 6 key features (leave blank if not needed)',
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def image_preview(self, obj):
        try:
            if obj.image:
                return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        except Exception:
            pass
        return "No image"
    image_preview.short_description = 'Preview'
    
    def product_count(self, obj):
        try:
            count = obj.products.count()
            if count > 0:
                return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
            return format_html('<span style="color: gray;">0</span>')
        except Exception:
            return format_html('<span style="color: gray;">-</span>')
    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'is_active', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 80px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'category', 'size', 'gsm', 'order', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    list_editable = ['order', 'is_active', 'is_featured']
    search_fields = ['title', 'description', 'category__title']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    autocomplete_fields = ['category']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'title', 'slug', 'description', 'image'),
            'description': 'Core product information'
        }),
        ('Product Specifications', {
            'fields': ('size', 'gsm', 'color', 'handle_type', 'price_range', 'minimum_order'),
            'description': 'Technical specifications and pricing',
            'classes': ('collapse',)
        }),
        ('Product Features', {
            'fields': ('feature_1', 'feature_2', 'feature_3', 'feature_4'),
            'description': 'Add up to 4 key features (leave blank if not needed)',
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active', 'is_featured')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'url', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'url']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'image', 'url')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_id', 'name', 'company_name', 'product_link', 'quantity', 'status_badge', 'created_at']
    list_filter = ['is_processed', 'created_at', 'product']
    search_fields = ['name', 'company_name', 'email', 'contact_number', 'id']
    readonly_fields = ['created_at', 'quote_summary']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    
    fieldsets = (
        ('Quote Information', {
            'fields': ('quote_summary',),
            'description': 'Quick overview of this quote request'
        }),
        ('Customer Information', {
            'fields': ('name', 'company_name', 'email', 'contact_number'),
            'description': 'Contact details for follow-up'
        }),
        ('Product Requirements', {
            'fields': ('product', 'size', 'gsm', 'quantity', 'message'),
            'description': 'Specific product requirements and specifications'
        }),
        ('Status & Tracking', {
            'fields': ('is_processed', 'created_at'),
            'description': 'Processing status and submission date'
        }),
    )
    
    def has_add_permission(self, request):
        # Disable manual adding of quotes (they should come from the form)
        return False
    
    def quote_id(self, obj):
        return f"Q-{obj.id:04d}"
    quote_id.short_description = "Quote ID"
    quote_id.admin_order_field = "id"
    
    def product_link(self, obj):
        if obj.product:
            return format_html('<a href="/product/{}" target="_blank">{}</a>', obj.product.slug, obj.product.title)
        return "—"
    product_link.short_description = "Product"
    product_link.admin_order_field = "product"
    
    def status_badge(self, obj):
        if obj.is_processed:
            return format_html('<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">✓ PROCESSED</span>')
        return format_html('<span style="background: #ffc107; color: #000; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">⏳ PENDING</span>')
    status_badge.short_description = "Status"
    status_badge.admin_order_field = "is_processed"
    
    def quote_summary(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #2D7A4E;">'
            '<h3 style="margin-top: 0; color: #2D7A4E;">Quote #{}</h3>'
            '<p><strong>Customer:</strong> {}{}</p>'
            '<p><strong>Contact:</strong> {} | {}</p>'
            '<p><strong>Product:</strong> {} (Qty: {})</p>'
            '<p><strong>Specs:</strong> {} | {}</p>'
            '<p><strong>Status:</strong> {}</p>'
            '</div>',
            obj.id,
            obj.name,
            f" ({obj.company_name})" if obj.company_name else "",
            obj.email,
            obj.contact_number,
            obj.product.title if obj.product else "N/A",
            obj.quantity,
            obj.size,
            obj.gsm,
            "Processed ✓" if obj.is_processed else "Pending ⏳"
        )
    quote_summary.short_description = "Quote Summary"
    
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(is_processed=True)
        self.message_user(request, f'{updated} quote(s) marked as processed.')
    mark_as_processed.short_description = "Mark selected quotes as processed"
    
    def mark_as_unprocessed(self, request, queryset):
        updated = queryset.update(is_processed=False)
        self.message_user(request, f'{updated} quote(s) marked as unprocessed.')
    mark_as_unprocessed.short_description = "Mark selected quotes as unprocessed"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'updated_at']
    list_filter = ['is_active', 'category']
    list_editable = ['order', 'is_active']
    search_fields = ['question', 'answer']
    
    fieldsets = (
        ('Question & Answer', {
            'fields': ('question', 'answer')
        }),
        ('Organization', {
            'fields': ('category', 'order', 'is_active')
        }),
    )
