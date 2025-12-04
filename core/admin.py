from django.contrib import admin
from django.utils.html import format_html
from .models import MenuItem, Product, Service, Quote, FAQ

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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description', 'category']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'description', 'image'),
            'description': 'Core product information displayed on the website'
        }),
        ('Product Specifications', {
            'fields': ('material', 'gsm_range', 'handle_type', 'customization'),
            'description': 'Technical specifications shown on product detail page',
            'classes': ('collapse',)
        }),
        ('Product Features', {
            'fields': ('feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5', 'feature_6'),
            'description': 'Add up to 6 key features (leave blank if not needed)',
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'description': 'Control visibility and ordering on the website'
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image"


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
