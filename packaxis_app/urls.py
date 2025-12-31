"""
URL configuration for packaxis_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.sitemaps import sitemap_view, robots_txt_view
from core.views import custom_404_view, custom_403_view, custom_500_view

urlpatterns = [
    # Admin path - use only one obscure path for security
    # Remove /admin/ to prevent easy discovery by attackers
    path('superusers/', admin.site.urls),
    # path('admin/', admin.site.urls),  # DISABLED for security
    path('', include('core.urls')),
    path('blog/', include('blog.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('sitemap.xml', sitemap_view, name='sitemap'),
    path('robots.txt', robots_txt_view, name='robots'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers - these are used when DEBUG=False
handler404 = custom_404_view
handler403 = custom_403_view
handler500 = custom_500_view
