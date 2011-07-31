from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template

from humfrey.misc.views import SimpleView

urlpatterns = patterns('',
)

handler404 = SimpleView(template_name='404-empty.html', context={'status_code':404})
handler500 = SimpleView(template_name='500.html', context={'status_code':500})
