"""library URL Configuration"""
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('auth/', include('authentication.urls', namespace='authentication')),
    
    # App URLs
    path('', include('book.urls', namespace='book')),
    path('orders/', include('order.urls', namespace='order')),
    path('authors/', include('author.urls')),
    
    # Alias for better user experience
    path('books/', include(('book.urls', 'book'), namespace='book_alias')),  # Allow /books/ as an alternative to /
    path('my-books/', lambda request: redirect('order:my_orders'), name='my_books'),
]

# Add static and media files URL patterns in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
