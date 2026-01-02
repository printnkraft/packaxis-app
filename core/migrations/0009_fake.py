# Generated manually to replace deleted 0009_create_new_product_model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_product_table'),
    ]

    operations = [
        # NOTE: Don't delete ProductOld - other models may reference it
        # It will be cleaned up in a separate migration if needed
        
        # Create new Product model with ALL fields at once
        # (no need for separate migration 0014)
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
                
                # Features (all 6)
                ('feature_1', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_2', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_3', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_4', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_5', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                ('feature_6', models.CharField(max_length=200, blank=True, help_text='Product feature')),
                
                # SEO & Metadata (moved from 0014)
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
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('review', models.TextField()),
                ('image', models.ImageField(blank=True, help_text='Optional review image', null=True, upload_to='review-images/')),
                ('is_verified', models.BooleanField(default=False, help_text='Verified purchase (auto-set if linked to order)')),
                ('is_approved', models.BooleanField(default=False, help_text='Approved to display')),
                ('helpful_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='core.product')),
            ],
            options={
                'verbose_name': 'Product Review',
                'verbose_name_plural': 'Product Reviews',
                'ordering': ['-created_at'],
            },
        ),
    ]
