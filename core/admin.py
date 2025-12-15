from django.contrib import admin
from django.utils.html import format_html
from .models import MenuItem, Product, ProductImage, ProductCategory, Service, Quote, FAQ, Industry, Cart, CartItem, Order, OrderItem

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
    list_display = ['image_preview', 'title', 'category', 'display_price_admin', 'stock_status', 'order', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'category', 'track_inventory', 'created_at']
    list_editable = ['order', 'is_active', 'is_featured']
    search_fields = ['title', 'description', 'category__title', 'sku']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    autocomplete_fields = ['category']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'title', 'slug', 'description', 'image'),
            'description': 'Core product information'
        }),
        ('E-Commerce Pricing', {
            'fields': ('price', 'compare_at_price', 'price_per', 'sku'),
            'description': 'Set price for e-commerce. Leave price blank to show price_range instead (quote mode).',
        }),
        ('Inventory Management', {
            'fields': ('stock_quantity', 'track_inventory', 'allow_backorder', 'case_quantity', 'minimum_order'),
            'description': 'Stock and inventory settings',
            'classes': ('collapse',)
        }),
        ('Product Specifications', {
            'fields': ('size', 'gsm', 'color', 'handle_type', 'weight', 'price_range'),
            'description': 'Technical specifications (price_range is shown if no e-commerce price set)',
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
    
    def display_price_admin(self, obj):
        if obj.price:
            if obj.compare_at_price and obj.compare_at_price > obj.price:
                return format_html(
                    '<span style="color: green; font-weight: bold;">${}</span> '
                    '<span style="text-decoration: line-through; color: #999;">${}</span>',
                    obj.price, obj.compare_at_price
                )
            return format_html('<span style="color: green; font-weight: bold;">${}</span>', obj.price)
        elif obj.price_range:
            return format_html('<span style="color: #666;">{}</span>', obj.price_range)
        return format_html('<span style="color: #999;">—</span>')
    display_price_admin.short_description = 'Price'
    
    def stock_status(self, obj):
        if not obj.track_inventory:
            return format_html('<span style="background: #6c757d; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">Not Tracked</span>')
        elif obj.stock_quantity > 10:
            return format_html('<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">In Stock ({})</span>', obj.stock_quantity)
        elif obj.stock_quantity > 0:
            return format_html('<span style="background: #ffc107; color: #000; padding: 2px 8px; border-radius: 10px; font-size: 11px;">Low Stock ({})</span>', obj.stock_quantity)
        else:
            if obj.allow_backorder:
                return format_html('<span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">Backorder</span>')
            return format_html('<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">Out of Stock</span>')
    stock_status.short_description = 'Stock'


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


# ============================================
# E-COMMERCE ADMIN
# ============================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price', 'total_price']
    can_delete = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_key_short', 'total_items', 'subtotal', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['session_key']
    readonly_fields = ['session_key', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'
    
    def session_key_short(self, obj):
        return obj.session_key[:20] + '...' if len(obj.session_key) > 20 else obj.session_key
    session_key_short.short_description = 'Session'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_title', 'product_sku', 'quantity', 'unit_price', 'total_price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'total', 'status_badge', 'payment_badge', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'email', 'first_name', 'last_name', 'phone', 'company_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'order_summary']
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    fieldsets = (
        ('Order Summary', {
            'fields': ('order_summary',),
        }),
        ('Order Status', {
            'fields': ('order_number', 'status', 'payment_status', 'payment_method', 'payment_id'),
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'company_name'),
        }),
        ('Shipping Address', {
            'fields': ('shipping_address_1', 'shipping_address_2', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'),
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount', 'total'),
        }),
        ('Shipping & Tracking', {
            'fields': ('tracking_number', 'tracking_url', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'processing': '#6f42c1',
            'shipped': '#0dcaf0',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        text_color = '#000' if obj.status in ['pending'] else '#fff'
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, text_color, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def payment_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.payment_status, '#6c757d')
        text_color = '#000' if obj.payment_status == 'pending' else '#fff'
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color, text_color, obj.get_payment_status_display().upper()
        )
    payment_badge.short_description = 'Payment'
    payment_badge.admin_order_field = 'payment_status'
    
    def order_summary(self, obj):
        items_html = ''.join([
            f'<li>{item.quantity}x {item.product_title} @ ${item.unit_price} = ${item.total_price}</li>'
            for item in obj.items.all()
        ])
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #2D7A4E;">'
            '<h3 style="margin-top: 0; color: #2D7A4E;">Order #{}</h3>'
            '<p><strong>Customer:</strong> {} {}{}</p>'
            '<p><strong>Contact:</strong> {} | {}</p>'
            '<p><strong>Shipping:</strong><br>{}</p>'
            '<p><strong>Items:</strong></p>'
            '<ul style="margin: 0; padding-left: 20px;">{}</ul>'
            '<p style="margin-top: 10px;"><strong>Total:</strong> ${}</p>'
            '</div>',
            obj.order_number,
            obj.first_name, obj.last_name,
            f" ({obj.company_name})" if obj.company_name else "",
            obj.email, obj.phone,
            obj.shipping_address.replace('\n', '<br>'),
            items_html,
            obj.total
        )
    order_summary.short_description = 'Order Summary'
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = "Mark as Processing"
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = "Mark as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark as Delivered"
