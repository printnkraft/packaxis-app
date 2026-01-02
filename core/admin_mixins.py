"""
Reusable mixins for Django admin customizations.

These mixins extract common admin patterns for:
- Hierarchical model display (categories, industries)
- Image preview displays
- Related object counts
"""

from django.contrib import admin
from django.utils.html import format_html


class HierarchyDisplayMixin:
    """
    Mixin for displaying hierarchical models with indentation based on depth level.
    
    Models using this mixin must have:
    - A 'parent' ForeignKey field (nullable, self-referencing)
    - A 'level' property that returns the nesting depth
    
    Usage:
        @admin.register(ProductCategory)
        class ProductCategoryAdmin(HierarchyDisplayMixin, admin.ModelAdmin):
            list_display = ['image_preview', 'title_with_level', 'parent', ...]
    """
    
    def title_with_level(self, obj):
        """Display title with indentation based on hierarchy level"""
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * obj.level
        return format_html(
            '{}<strong>{}</strong>',
            format_html(indent),
            obj.title
        )
    
    title_with_level.short_description = 'Title'
    title_with_level.admin_order_field = 'title'


class ImagePreviewMixin:
    """
    Mixin for displaying image field previews as thumbnails in admin list view.
    
    Models using this mixin must have an 'image' field.
    
    Usage:
        @admin.register(ProductCategory)
        class ProductCategoryAdmin(ImagePreviewMixin, admin.ModelAdmin):
            list_display = ['image_preview', 'title', ...]
    """
    
    def image_preview(self, obj):
        """Display a thumbnail preview of the image field"""
        try:
            if obj.image:
                return format_html(
                    '<img src="{}" style="max-height: 50px; max-width: 50px; '
                    'object-fit: cover; border-radius: 8px;" />',
                    obj.image.url
                )
        except Exception:
            pass
        return "No image"
    
    image_preview.short_description = 'Preview'


class CountDisplayMixin:
    """
    Mixin for displaying related object counts with color coding.
    
    Provides a helper method to display counts in green (> 0) or gray (= 0).
    
    Usage:
        class MyAdmin(CountDisplayMixin, admin.ModelAdmin):
            def related_count(self, obj):
                return self.colored_count(obj.related_items.count(), 'items')
    """
    
    def colored_count(self, count, label='items'):
        """
        Display a count with color coding.
        
        Args:
            count (int): The count to display
            label (str): Optional label for the count (for accessibility)
        
        Returns:
            HTML formatted count (green if > 0, gray if 0)
        """
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                count
            )
        return format_html(
            '<span style="color: gray;">0</span>'
        )
