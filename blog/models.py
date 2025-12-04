from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Blog post category"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    """Blog post model with SEO optimization fields"""
    
    title = models.CharField(max_length=200, help_text="Blog post title")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly version of title")
    
    # Content fields
    excerpt = models.TextField(max_length=300, help_text="Short description for post preview")
    content = models.TextField(help_text="Full blog post content (supports HTML)")
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True, help_text="Featured image for post")
    
    # SEO fields
    meta_description = models.CharField(max_length=160, help_text="SEO meta description (160 chars max)")
    meta_keywords = models.CharField(max_length=200, blank=True, help_text="Comma-separated keywords")
    
    # Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    # Author and dates
    author = models.CharField(max_length=100, default="PackAxis Team")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(default=timezone.now, help_text="Date to publish post")
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Analytics
    view_count = models.IntegerField(default=0, help_text="Number of views")
    
    class Meta:
        ordering = ['-publish_date']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
