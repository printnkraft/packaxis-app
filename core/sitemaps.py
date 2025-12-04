from django.http import HttpResponse
from django.urls import reverse
from core.models import Product
from blog.models import Post
from django.utils import timezone


def sitemap_view(request):
    """Generate dynamic sitemap.xml"""
    
    # Build sitemap XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Homepage
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/</loc>\n'
    xml_content += '    <priority>1.0</priority>\n'
    xml_content += '    <changefreq>weekly</changefreq>\n'
    xml_content += '  </url>\n'
    
    # Products page
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/products/</loc>\n'
    xml_content += '    <priority>0.9</priority>\n'
    xml_content += '    <changefreq>weekly</changefreq>\n'
    xml_content += '  </url>\n'
    
    # Individual products
    products = Product.objects.filter(is_active=True)
    for product in products:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>https://packaxis.ca/product/{product.slug}/</loc>\n'
        xml_content += '    <priority>0.8</priority>\n'
        xml_content += '    <changefreq>monthly</changefreq>\n'
        xml_content += '  </url>\n'
    
    # Pricing brochure
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/pricing-brochure/</loc>\n'
    xml_content += '    <priority>0.8</priority>\n'
    xml_content += '    <changefreq>monthly</changefreq>\n'
    xml_content += '  </url>\n'
    
    # FAQ
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/faq/</loc>\n'
    xml_content += '    <priority>0.8</priority>\n'
    xml_content += '    <changefreq>monthly</changefreq>\n'
    xml_content += '  </url>\n'
    
    # Blog
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/blog/</loc>\n'
    xml_content += '    <priority>0.9</priority>\n'
    xml_content += '    <changefreq>weekly</changefreq>\n'
    xml_content += '  </url>\n'
    
    # Blog posts
    blog_posts = Post.objects.filter(status='published', publish_date__lte=timezone.now())
    for post in blog_posts:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>https://packaxis.ca/blog/{post.slug}/</loc>\n'
        xml_content += f'    <lastmod>{post.updated_at.strftime("%Y-%m-%d")}</lastmod>\n'
        xml_content += '    <priority>0.7</priority>\n'
        xml_content += '    <changefreq>monthly</changefreq>\n'
        xml_content += '  </url>\n'
    
    # Quote request
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/quote/</loc>\n'
    xml_content += '    <priority>0.9</priority>\n'
    xml_content += '    <changefreq>yearly</changefreq>\n'
    xml_content += '  </url>\n'
    
    # Privacy & Terms
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/privacy-policy/</loc>\n'
    xml_content += '    <priority>0.3</priority>\n'
    xml_content += '    <changefreq>yearly</changefreq>\n'
    xml_content += '  </url>\n'
    
    xml_content += '  <url>\n'
    xml_content += '    <loc>https://packaxis.ca/terms-of-service/</loc>\n'
    xml_content += '    <priority>0.3</priority>\n'
    xml_content += '    <changefreq>yearly</changefreq>\n'
    xml_content += '  </url>\n'
    
    xml_content += '</urlset>'
    
    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt_view(request):
    """Generate robots.txt"""
    
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Sitemaps",
        "Sitemap: https://packaxis.ca/sitemap.xml",
        "",
        "# Disallow admin",
        "Disallow: /superusers/",
        "",
        "# Crawl delay",
        "Crawl-delay: 10",
    ]
    
    return HttpResponse("\n".join(lines), content_type="text/plain")
