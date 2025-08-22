"""
URL configuration for petshop project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
import os

def health_check(request):
    """Health check endpoint for Docker health checks"""
    return JsonResponse({'status': 'ok'})

def debug_media(request):
    """Debug endpoint to check media files"""
    try:
        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')
        
        debug_info = {
            'media_root': str(media_root),
            'products_dir': str(products_dir),
            'media_root_exists': os.path.exists(media_root),
            'products_dir_exists': os.path.exists(products_dir),
            'base_dir': str(settings.BASE_DIR),
        }
        
        if os.path.exists(products_dir):
            debug_info['products_files'] = os.listdir(products_dir)
        else:
            debug_info['products_files'] = 'Directory does not exist'
            
        if os.path.exists('/app/images'):
            debug_info['app_images_files'] = os.listdir('/app/images')
        else:
            debug_info['app_images_files'] = '/app/images does not exist'
            
        return JsonResponse(debug_info)
    except Exception as e:
        return JsonResponse({'error': str(e)})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('debug/media/', debug_media, name='debug_media'),
    path('', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
]

# Serve media files in production
from django.views.static import serve
from django.urls import re_path

# Force media serving in production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Serve static files only in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 