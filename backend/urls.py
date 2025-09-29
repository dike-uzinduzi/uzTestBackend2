from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('api/',include('djoser.urls')),
    path('api/',include('users.urls')),
    path('api/',include('albums.urls')),
    path('api/',include('payments.urls')),
     path('api/notifications/', include('notifications.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)