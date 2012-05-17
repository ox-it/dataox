from django.conf.urls.defaults import patterns, url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib.auth import views as auth_views
from django_webauth.views import LogoutView

from humfrey.desc import views as desc_views
from humfrey.misc import views as misc_views

from dataox.equipment import views as equipment_views

from humfrey.misc.views import SimpleView

mapping_kwargs = {'id_mapping': (),
                  'doc_view': ('equipment', 'doc-generic'),
                  'desc_view': ('equipment', 'desc')}

urlpatterns = patterns('',
    url(r'^search/$', equipment_views.SearchView.as_view(**mapping_kwargs), name='search'),

    (r'^view/$', equipment_views.DocView.as_view(**mapping_kwargs), {}, 'doc-generic'),
    #(r'^view.+$', equipment_views.DocView.as_view(**mapping_kwargs), {}, 'doc'),
    (r'^desc/$', equipment_views.DescView.as_view(**mapping_kwargs), {}, 'desc'),

    url(r'^browse/(?:(?P<notation>[a-z\-\d\/]+)/)?$', equipment_views.BrowseView.as_view(**mapping_kwargs), name='browse'),

    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^webauth/', include('django_webauth.urls', 'webauth')),

    url(r'^$', misc_views.SimpleView.as_view(template_name="equipment/index"), name='index'),
    url(r'^about/$', misc_views.SimpleView.as_view(template_name="equipment/about"), name='about'),
    url(r'^contact/$', misc_views.SimpleView.as_view(template_name="equipment/contact"), name='contact'),

) + staticfiles_urlpatterns()

handler404 = SimpleView.as_view(template_name='404-main', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})
