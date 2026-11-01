"""
RecyConnect URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.svg', permanent=True)),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('scrap/', include('scrap.urls')),
    path('pickups/', include('pickups.urls')),
    path('transactions/', include('transactions.urls')),
    path('recyclers/', include('recyclers.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
