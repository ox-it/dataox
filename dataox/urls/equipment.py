from django.conf.urls.defaults import patterns, url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dataox.equipment import views as equipment_views

from humfrey.misc.views import SimpleView
urlpatterns = patterns('',
    url(r'^$', equipment_views.SearchView.as_view()),
    url(r'^item:(?P<id>[\da-f]+)/$', equipment_views.ItemView.as_view(), name="item")
) + staticfiles_urlpatterns()

handler404 = SimpleView.as_view(template_name='404-main', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})
