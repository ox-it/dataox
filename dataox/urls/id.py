from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views
from humfrey.misc.views import SimpleView

urlpatterns = patterns('',
    url(r'^.*', desc_views.IdView.as_view(), {}, 'id'),
) + staticfiles_urlpatterns()

handler404 = SimpleView.as_view(template_name='404', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})
