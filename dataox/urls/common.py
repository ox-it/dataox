from django.conf import settings
from django.conf.urls import patterns, url, include 
from django.contrib import admin
from humfrey.misc import views as misc_views
from dataox.core import views as core_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

__all__ = ['handler404', 'handler500', 'handler503', 'common_urlpatterns']

handler404 = misc_views.SimpleView.as_view(template_name='404', context={'status_code':404})
handler500 = core_views.ServerErrorView.as_view()
handler503 = core_views.MaintenanceModeView.as_view()

common_urlpatterns = []

if settings.DEBUG:
    import debug_toolbar
    common_urlpatterns += staticfiles_urlpatterns()
    common_urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
