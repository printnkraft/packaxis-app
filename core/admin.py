from django.contrib import admin
from django.utils.html import format_html
from django.core.cache import cache
from .models import (
    MenuItem, Product, ProductImage, ProductCategory, Service, Quote, FAQ, Industry, 
    Cart, CartItem, Order, OrderItem, ProductVariant, TieredPricing, DiscountRule, 
    ProductReview, UseCase, ProductUseCase, ProductIndustry, SiteSettings, PromoCode, Tag
)

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
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Invalidate menu cache when menu items change
        cache.delete('top_level_menu_items')
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # Invalidate menu cache when menu items are deleted
        cache.delete('top_level_menu_items')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title_with_level', 'parent', 'description', 'product_count', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    autocomplete_fields = ['parent']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'image', 'parent'),
            'description': 'Core category information displayed on the website. Set parent for nested sub-categories.'
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
    
    def title_with_level(self, obj):
        """Show category with indentation based on hierarchy level"""
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * obj.level
        return format_html('{}<strong>{}</strong>', format_html(indent), obj.title)
    title_with_level.short_description = 'Category'
    title_with_level.admin_order_field = 'title'
    
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
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Invalidate product categories cache when categories change
        cache.delete('active_product_categories')
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # Invalidate product categories cache when categories are deleted
        cache.delete('active_product_categories')


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


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['variant_type', 'name', 'sku_suffix', 'price_adjustment', 'stock_quantity', 'image', 'is_active']
    

class TieredPricingInline(admin.TabularInline):
    model = TieredPricing
    extra = 1
    fields = ['min_quantity', 'max_quantity', 'price_per_unit', 'label']
    

class ProductIndustryInline(admin.TabularInline):
    model = ProductIndustry
    extra = 1
    fields = ['industry']
    autocomplete_fields = ['industry']


class ProductUseCaseInline(admin.TabularInline):
    model = ProductUseCase
    extra = 1
    fields = ['use_case', 'is_enabled', 'order']
    autocomplete_fields = ['use_case']
    verbose_name = "Use Case"
    verbose_name_plural = "Use Cases (Enable/Disable for this Product)"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "use_case":
            kwargs["queryset"] = UseCase.objects.filter(is_active=True).order_by('order', 'title')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_formset(self, request, obj=None, **kwargs):
        """
        Provide help text to guide users in adding use cases
        """
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            # Count existing use cases for this product
            existing_count = obj.product_use_cases.count()
            total_available = UseCase.objects.filter(is_active=True).count()
            formset.help_text = f"Currently {existing_count} of {total_available} available use cases are configured for this product. Click 'Add another Use Case' to enable more."
        return formset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'display_categories', 'display_tags', 'display_price_admin', 'stock_status', 'review_stats', 'order', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'categories', 'tags', 'track_inventory', 'created_at']
    list_editable = ['order', 'is_active', 'is_featured']
    search_fields = ['title', 'description', 'categories__title', 'sku', 'tags__name']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    filter_horizontal = ['categories', 'tags']
    inlines = [ProductImageInline, ProductVariantInline, TieredPricingInline, ProductIndustryInline, ProductUseCaseInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('categories', 'title', 'slug', 'description', 'image', 'tags'),
            'description': 'Core product information. Select multiple categories if product fits in more than one. Use tags for flexible filtering and organization.'
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
            'fields': ('feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5', 'feature_6'),
            'description': 'Add up to 6 key features (leave blank if not needed)',
            'classes': ('collapse',)
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'canonical_url', 'search_keywords', 'schema_type'),
            'description': 'Search engine optimization fields',
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
    
    def review_stats(self, obj):
        try:
            count = obj.review_count
            if count > 0:
                avg = obj.average_rating
                return format_html('<span style="color: #ffc107;">★</span> {} ({} reviews)', avg, count)
            return format_html('<span style="color: #999;">No reviews</span>')
        except Exception:
            return format_html('<span style="color: #999;">—</span>')
    review_stats.short_description = 'Reviews'
    
    def display_tags(self, obj):
        """Display product tags with colors"""
        tags = obj.tags.filter(is_active=True)[:5]  # Show first 5 tags
        if not tags:
            return format_html('<span style="color: #999;">No tags</span>')
        
        tag_html = ''.join([
            format_html(
                '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-right: 4px; display: inline-block;">{}</span>',
                tag.color, tag.name
            ) for tag in tags
        ])
        
        total_tags = obj.tags.filter(is_active=True).count()
        if total_tags > 5:
            tag_html += format_html('<span style="color: #999; font-size: 10px;">+{} more</span>', total_tags - 5)
        
        return format_html(tag_html)
    display_tags.short_description = 'Tags'
    
    def display_categories(self, obj):
        """Display product categories"""
        categories = obj.categories.all()[:3]  # Show first 3 categories
        if not categories:
            return format_html('<span style="color: #999;">No categories</span>')
        
        cat_html = ', '.join([
            format_html('<span style="font-weight: 500;">{}</span>', cat.title) 
            for cat in categories
        ])
        
        total_cats = obj.categories.count()
        if total_cats > 3:
            cat_html += format_html(' <span style="color: #999; font-size: 10px;">+{} more</span>', total_cats - 3)
        
        return format_html(cat_html)
    display_categories.short_description = 'Categories'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'rating_display', 'is_verified', 'is_approved', 'order', 'created_at']
    list_filter = ['is_approved', 'is_verified', 'rating', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['product__title', 'name', 'email', 'review', 'order__order_number']
    autocomplete_fields = ['product', 'order']
    list_per_page = 25
    
    fieldsets = (
        ('Review Details', {
            'fields': ('product', 'order', 'name', 'email', 'rating', 'title', 'review', 'image')
        }),
        ('Verification', {
            'fields': ('is_verified', 'is_approved'),
            'description': 'Reviews linked to delivered orders are automatically verified'
        }),
    )
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_display.short_description = 'Rating'


@admin.register(UseCase)
class UseCaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon_name', 'order', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'icon_name', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    list_per_page = 25
    
    fieldsets = (
        ('Use Case Information', {
            'fields': ('title', 'description', 'icon_name'),
            'description': 'Create global use cases that can be assigned to products'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'description': 'Control visibility and display order'
        }),
    )
    
    def product_count(self, obj):
        count = obj.use_case_products.filter(is_enabled=True).count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    product_count.short_description = 'Enabled in Products'


@admin.register(DiscountRule)
class DiscountRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'product', 'discount_percentage', 'discount_amount', 'is_active', 'start_date', 'end_date']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    list_editable = ['is_active']
    search_fields = ['name', 'promo_code', 'product__title']
    autocomplete_fields = ['product']
    
    fieldsets = (
        ('Discount Details', {
            'fields': ('name', 'discount_type', 'discount_percentage', 'discount_amount', 'promo_code')
        }),
        ('Applicable To', {
            'fields': ('product', 'min_quantity', 'customer_group')
        }),
        ('Validity', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )


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
    list_display = ['image_preview', 'title_with_level', 'parent', 'url', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'url']
    list_per_page = 20
    autocomplete_fields = ['parent']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'image', 'url', 'parent'),
            'description': 'Set parent for nested sub-industries (e.g., Food Service > Restaurants > Fast Food)'
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
    
    def title_with_level(self, obj):
        """Show industry with indentation based on hierarchy level"""
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * obj.level
        return format_html('{}<strong>{}</strong>', format_html(indent), obj.title)
    title_with_level.short_description = 'Industry'
    title_with_level.admin_order_field = 'title'


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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['color_preview', 'name', 'slug', 'product_count_display', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'color'),
            'description': 'Create tags for product filtering and organization (similar to Shopify tags)'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def color_preview(self, obj):
        """Show tag with its color"""
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">{}</span>',
            obj.color, obj.name
        )
    color_preview.short_description = 'Tag'
    color_preview.admin_order_field = 'name'
    
    def product_count_display(self, obj):
        """Show number of products with this tag"""
        count = obj.get_product_count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{} products</span>', count)
        return format_html('<span style="color: gray;">0 products</span>')
    product_count_display.short_description = 'Usage'


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
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount', 'promo_code', 'total'),
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
        updated = queryset.update(status='processing', tracking_step=2)
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = "Mark as Processing"
    
    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='shipped', tracking_step=3, shipped_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = "Mark as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='delivered', tracking_step=4, delivered_at=timezone.now())
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark as Delivered"


# ============================================
# PROMO CODE ADMIN
# ============================================

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_display', 'usage_display', 'is_active', 'valid_until', 'created_at']
    list_filter = ['is_active', 'discount_type', 'first_order_only', 'created_at']
    list_editable = ['is_active']
    search_fields = ['code', 'description']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Code Details', {
            'fields': ('code', 'description', 'is_active'),
        }),
        ('Discount Settings', {
            'fields': ('discount_type', 'discount_value', 'maximum_discount'),
            'description': 'Configure the discount amount. For percentage, enter value like 10 for 10% off.'
        }),
        ('Usage Limits', {
            'fields': ('minimum_order_amount', 'usage_limit', 'usage_count', 'per_user_limit'),
            'classes': ('collapse',)
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until'),
            'classes': ('collapse',)
        }),
        ('Restrictions', {
            'fields': ('first_order_only',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        elif obj.discount_type == 'fixed':
            return f"${obj.discount_value}"
        else:
            return "Free Shipping"
    discount_display.short_description = 'Discount'
    
    def usage_display(self, obj):
        if obj.usage_limit:
            return f"{obj.usage_count}/{obj.usage_limit}"
        return f"{obj.usage_count}/∞"
    usage_display.short_description = 'Usage'


# ============================================
# SITE SETTINGS ADMIN
# ============================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'online_payments_enabled', 'tax_rate', 'updated_at']
    
    fieldsets = (
        ('Payment Settings', {
            'fields': ('online_payments_enabled',),
            'description': 'Control online payment functionality'
        }),
        ('Store Information', {
            'fields': ('store_name', 'store_email', 'store_phone', 'store_address'),
            'classes': ('collapse',)
        }),
        ('Order Settings', {
            'fields': ('tax_rate', 'minimum_order_amount', 'free_shipping_threshold'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        # Auto-redirect to the single settings instance
        settings = SiteSettings.get_settings()
        from django.shortcuts import redirect
        return redirect(f'/admin/core/sitesettings/{settings.pk}/change/')
