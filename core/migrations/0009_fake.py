# Generated manually to replace deleted 0009_create_new_product_model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_product_table'),
    ]

    operations = [
        # Create new Product model with base fields
        # (inventory and pricing fields will be added in migration 0013)
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, help_text='Product name (e.g., 10x12x5 Brown Kraft Bag)')),
                ('description', models.TextField(blank=True, help_text='Product description (optional)')),
                ('image', models.ImageField(upload_to='products/', help_text='Product image')),
                ('slug', models.SlugField(unique=True, help_text='URL-friendly version of title (auto-generated)')),
                
                # Product specifications
                ('size', models.CharField(max_length=100, blank=True, help_text='e.g., 10x12x5 inches')),
                ('gsm', models.CharField(max_length=50, blank=True, help_text='e.g., 120 GSM')),
                ('color', models.CharField(max_length=100, blank=True, help_text='e.g., Brown, White, Custom')),
                ('handle_type', models.CharField(max_length=200, blank=True, help_text='e.g., Twisted, Flat, No Handle')),
                
                # Legacy fields
                ('price_range', models.CharField(max_length=100, blank=True, help_text='e.g., $0.50 - $1.00 per piece')),
                ('minimum_order', models.IntegerField(null=True, blank=True, help_text='Minimum order quantity')),
                
                # Features
                ('feature_1', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_2', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_3', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_4', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_5', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_6', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                
                # SEO & Metadata
                ('meta_title', models.CharField(max_length=70, blank=True, help_text='SEO title (max 70 chars)')),
                ('meta_description', models.CharField(max_length=160, blank=True, help_text='SEO description (max 160 chars)')),
                ('canonical_url', models.URLField(blank=True, help_text='Canonical URL if different from default')),
                ('search_keywords', models.TextField(blank=True, help_text='Internal search keywords (comma-separated)')),
                ('schema_type', models.CharField(max_length=50, default='Product', help_text='Schema.org type')),
                
                # Display settings
                ('order', models.IntegerField(default=0, help_text='Display order within category (lower numbers appear first)')),
                ('is_active', models.BooleanField(default=True, help_text='Show/hide this product')),
                ('is_featured', models.BooleanField(default=False, help_text='Feature on homepage')),
                
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                
                # Foreign key
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='core.productcategory', help_text='Product category')),
            ],
            options={
                'ordering': ['category__order', 'order', 'title'],
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['slug'], name='core_product_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'is_active'], name='core_product_cat_active_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active', 'is_featured'], name='core_product_active_feat_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active', 'order'], name='core_product_active_ord_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['created_at'], name='core_product_created_idx'),
        ),
    ]
