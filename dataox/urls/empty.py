from django.conf.urls.defaults import patterns

from humfrey.misc.views import SimpleView

urlpatterns = patterns('',
)

handler404 = SimpleView(template_name='404-empty', context={'status_code':404})
handler500 = SimpleView(template_name='500', context={'status_code':500})
