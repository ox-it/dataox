from django.conf.urls.defaults import patterns, url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib.auth import views as auth_views
from django_webauth.views import LogoutView

from dataox.equipment import views as equipment_views

from humfrey.misc.views import SimpleView
urlpatterns = patterns('',
    url(r'^$', equipment_views.SearchView.as_view(), name='index'),
    url(r'^item:(?P<id>[\da-f]+)/$', equipment_views.ItemView.as_view(), name="item"),
    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^webauth/', include('django_webauth.urls', 'webauth')),
) + staticfiles_urlpatterns()

handler404 = SimpleView.as_view(template_name='404-main', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})
