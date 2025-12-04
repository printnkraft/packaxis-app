# Blog Deployment Guide for PythonAnywhere

## Overview
A complete blog section has been added to your PackAxis website with 4 SEO-optimized posts covering paper bag topics.

## What Was Added

### Blog Features
- **Post Management**: Full CRUD through Django admin at packaxis.ca/superusers
- **Categories**: 4 categories (Sustainability, Printing & Design, Business Tips, Industry News)
- **SEO Optimization**: Meta descriptions, keywords, schema.org BlogPosting markup
- **View Counter**: Tracks post popularity
- **Related Posts**: Shows similar articles on post detail pages
- **Pagination**: 9 posts per page on blog list
- **Category Filtering**: Filter posts by category
- **Responsive Design**: Mobile-optimized layout

### Initial Blog Posts Created
1. **Why Choose Paper Bags Over Plastic?** (Sustainability)
   - Environmental benefits, biodegradability, business advantages
   - Slug: `/blog/why-choose-paper-bags-over-plastic/`

2. **Custom Paper Bag Printing Guide** (Printing & Design)
   - Design tips, color psychology, printing methods, cost optimization
   - Slug: `/blog/custom-paper-bag-printing-guide/`

3. **How to Choose the Right Paper Bag Size** (Business Tips)
   - Size chart guide, weight capacity, industry-specific recommendations
   - Slug: `/blog/choose-right-paper-bag-size/`

4. **Canada's Plastic Ban 2025** (Industry News)
   - Regulations, compliance requirements, transition strategies
   - Slug: `/blog/canada-plastic-ban-2025/`

## Deployment Steps

### 1. Pull Latest Code on PythonAnywhere
```bash
cd ~/packaxis-website
git pull origin main
```

### 2. Install New Dependencies (if needed)
```bash
pip install Pillow --user
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Blog Posts on Production
Since the database is separate, run the blog post creation script:
```bash
python create_blog_posts.py
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. Reload Web App
Go to PythonAnywhere Web tab and click the green **Reload** button for webapp-2845519.pythonanywhere.com

## Accessing the Blog

### Public URLs
- Blog list: `https://packaxis.ca/blog/`
- Individual posts: `https://packaxis.ca/blog/<slug>/`
- Category filter: `https://packaxis.ca/blog/?category=<category-slug>`

### Admin Management
1. Go to `https://packaxis.ca/superusers`
2. Login with admin credentials
3. Navigate to **Blog Posts** or **Categories**
4. Add, edit, or delete posts as needed

## Creating New Blog Posts

### Via Django Admin (Recommended)
1. Login to admin panel
2. Click **Blog Posts** → **Add Blog Post**
3. Fill in required fields:
   - **Title**: Post title (slug auto-generates)
   - **Category**: Select from dropdown
   - **Excerpt**: 300 character summary
   - **Content**: Full HTML content (use rich editor)
   - **Meta Description**: 160 characters for SEO
   - **Meta Keywords**: Comma-separated
   - **Featured Image**: Optional (upload to media/blog/)
   - **Status**: Draft or Published
   - **Publish Date**: Schedule publication
4. Save

### Content Tips for SEO
- **Title**: Include target keyword, keep under 60 characters
- **Excerpt**: Compelling summary with keyword
- **Meta Description**: Include keyword naturally, call to action
- **Meta Keywords**: 5-10 relevant terms
- **Content**: 
  - Use H2/H3 headings with keywords
  - Include internal links to products/services
  - Add external authoritative links
  - Aim for 1500-2500 words for best SEO
  - Use bullet points and short paragraphs

### HTML Formatting in Content
```html
<h2>Main Section Heading</h2>
<p>Paragraph text with <strong>bold emphasis</strong> and <em>italic text</em>.</p>

<h3>Subsection Heading</h3>
<ul>
  <li>Bullet point item</li>
  <li>Another item</li>
</ul>

<blockquote>
  <p>Quote or important callout</p>
</blockquote>

<a href="https://example.com">External link</a>
<a href="{% url 'core:products' %}">Internal link to products</a>
```

## Blog Post Ideas for Future

### Sustainability Series
- "The Complete Guide to Compostable vs Recyclable Paper Bags"
- "How Paper Bags Reduce Your Business's Carbon Footprint"
- "FSC Certification: What It Means for Your Paper Bags"

### Design & Branding
- "10 Paper Bag Design Mistakes to Avoid"
- "Color Psychology in Retail Packaging: What Your Bag Color Says"
- "Case Study: How Custom Bags Increased Brand Recognition by 45%"

### Business Operations
- "Cost Comparison: Paper vs Plastic Bags for Canadian Retailers"
- "Storage and Handling Best Practices for Bulk Paper Bags"
- "How to Calculate Your Paper Bag Requirements"

### Industry & Trends
- "2025 Packaging Trends: What Canadian Retailers Need to Know"
- "The Rise of Reusable Shopping Bags: Impact on Paper Bag Demand"
- "Provincial Plastic Ban Comparison Across Canada"

### Product Guides
- "Square Bottom vs Flat Bottom: Which Paper Bag Is Right for You?"
- "Understanding GSM: Paper Weight Guide for Businesses"
- "Handle Options for Paper Bags: Pros and Cons"

## SEO Optimization Checklist

For each new post:
- [ ] Title includes primary keyword
- [ ] Meta description 150-160 characters
- [ ] At least 3 H2 headings with keywords
- [ ] Internal links to 2-3 pages (products, quote, other posts)
- [ ] External link to 1-2 authoritative sources
- [ ] Featured image with descriptive alt text
- [ ] Meta keywords include variations
- [ ] URL slug is keyword-rich and readable
- [ ] Content is 1500+ words
- [ ] Publish date is current

## Adding Categories

In Django admin:
1. Go to **Categories** → **Add Category**
2. Enter **Name** (slug auto-generates)
3. Add **Description** (optional, shows on category filter page)
4. Save

Example categories to add:
- Customer Success Stories
- How-To Guides
- Packaging Tips
- Seasonal Ideas
- Industry Research

## Managing Featured Images

### Upload Process
1. Prepare image: 1200x600px minimum, optimized (under 200KB)
2. In blog post admin, click **Choose File** under Featured Image
3. Upload image (saves to `media/blog/`)
4. Image displays on blog list and post detail pages

### Image Requirements
- Format: JPG, PNG, WebP
- Dimensions: 1200x600px recommended (2:1 ratio)
- File size: Under 200KB for fast loading
- Alt text: Automatically uses post title

## Troubleshooting

### Blog posts don't show up
- Check post **Status** is "Published"
- Verify **Publish Date** is not in future
- Clear browser cache

### Images not displaying
- Run `python manage.py collectstatic`
- Verify `MEDIA_URL` and `MEDIA_ROOT` in settings.py
- Check file was uploaded to `media/blog/`

### Styling issues
- Clear browser cache
- Check `collectstatic` was run after template changes
- Verify CSS file path in template

## Analytics Tracking

Each post tracks:
- **View Count**: Increments on every page view
- **Publish Date**: For tracking performance over time
- **Category**: For analyzing popular topics

To view analytics:
1. Login to admin
2. Sort posts by **View Count** descending
3. Identify top performers
4. Create more content on similar topics

## Maintenance Schedule

**Weekly**:
- Check for new comment spam (if comments enabled)
- Review analytics in admin
- Share new posts on social media

**Monthly**:
- Publish 2-4 new blog posts
- Update old posts with new information
- Add internal links from new posts to old posts

**Quarterly**:
- Review top performing posts
- Update outdated information (regulations, statistics)
- Refresh meta descriptions for better CTR

## Next Steps

1. **Deploy to production** (follow steps above)
2. **Test blog functionality** on packaxis.ca/blog/
3. **Share posts** on social media channels
4. **Submit sitemap** to Google Search Console (we'll create sitemap.xml next)
5. **Monitor performance** in Google Analytics
6. **Create content calendar** for regular publishing

## Technical Details

### Models
- `Category`: name, slug, description
- `Post`: title, slug, content, excerpt, featured_image, meta_description, meta_keywords, category, author, publish_date, status, view_count

### Views
- `blog_list`: Paginated post list with category filtering
- `post_detail`: Individual post with related posts and view tracking

### Templates
- `blog/blog.html`: Blog list page with sidebar
- `blog/blog-post.html`: Post detail with schema.org markup

### URLs
- `/blog/` - Blog list
- `/blog/<slug>/` - Individual post
- `/blog/?category=<slug>` - Category filter

## Support

For questions or issues:
- Check Django admin logs
- Review PythonAnywhere error logs
- Email: hello@packaxis.ca

---

**Blog is now ready for production!** 🚀

All files committed to GitHub (commit 217222b)
Ready to deploy to PythonAnywhere following the steps above.
