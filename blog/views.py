from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Post, Category


def blog_list(request):
    """Display list of published blog posts"""
    
    # Get category filter from query params
    category_slug = request.GET.get('category')
    
    # Get published posts
    posts = Post.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).select_related('category')
    
    # Filter by category if specified
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
        selected_category = get_object_or_404(Category, slug=category_slug)
    else:
        selected_category = None
    
    # Pagination
    paginator = Paginator(posts, 9)  # 9 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
    }
    
    return render(request, 'blog/blog.html', context)


def post_detail(request, slug):
    """Display individual blog post"""
    
    post = get_object_or_404(
        Post,
        slug=slug,
        status='published',
        publish_date__lte=timezone.now()
    )
    
    # Increment view count
    post.increment_views()
    
    # Get related posts (same category, excluding current post)
    related_posts = Post.objects.filter(
        status='published',
        publish_date__lte=timezone.now(),
        category=post.category
    ).exclude(id=post.id)[:3]
    
    # Get recent posts for sidebar
    recent_posts = Post.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).exclude(id=post.id)[:5]
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'blog/blog-post.html', context)
