from django.conf.urls import patterns, url

from humfrey.misc import views as misc_views 

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='staging/index')),
)

handler404 = misc_views.SimpleView.as_view(template_name='404', context={'status_code':404})
handler500 = misc_views.SimpleView.as_view(template_name='500', context={'status_code':500})
