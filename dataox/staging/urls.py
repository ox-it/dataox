from django.conf.urls.defaults import patterns, url

from humfrey.misc import views as misc_views 

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='staging/index')),
)