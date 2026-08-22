from django.conf import settings
from django.conf.urls.static import static as static_url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.templatetags.static import static as static_file
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('dashboard/', include('adminpanel.urls')),
    path(
        'admin-login/',
        auth_views.LoginView.as_view(template_name='adminpanel/login.html'),
        name='admin_login',
    ),
    path(
        'favicon.ico', RedirectView.as_view(url=static_file('images/favicon.ico'))
    ),
]

if settings.DEBUG:
    urlpatterns += static_url(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )