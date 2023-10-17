from cms.sitemaps import CMSSitemap
from django.contrib import admin
from django.urls import path
from django.urls import re_path, include
from django.contrib.sitemaps.views import sitemap 
from django.views.generic.base import TemplateView

from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

from .sitemaps import StaticViewSitemap
sitemaps = {
    'static': StaticViewSitemap,
    'cmspages': CMSSitemap
}

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    path(r'precios/', include('precios.urls', namespace='precios')),
    re_path('accounts/', include('allauth.urls')),
    re_path(r'^members/', include(('members.urls', 'members'), namespace='members')),
    re_path(r'', include('djangocms_forms.urls')),
    re_path(r'^', include('cms.urls')),

    
    # re_path(r'^newsletter/', include('newsletter.urls')),
    re_path(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^robots.txt$',TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),),



]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    re_path(r'^currencies/', include('currencies.urls')),
] + urlpatterns

if settings.DEBUG:
    import debug_toolbar
    
    urlpatterns = [
        re_path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns