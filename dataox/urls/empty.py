from django.conf.urls.defaults import patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.misc.views import SimpleView

urlpatterns = patterns('',
) + staticfiles_urlpatterns()

handler404 = SimpleView.as_view(template_name='404-empty', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})
