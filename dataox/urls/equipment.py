from django.conf.urls.defaults import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib.auth import views as auth_views
from django_webauth.views import LogoutView

from humfrey.misc import views as misc_views

from dataox.equipment import views as equipment_views

from .main import handler404, handler500

urlpatterns = patterns('',
    url(r'^search/$', equipment_views.SearchView.as_view(), name='search'),

    url(r'^view/$', equipment_views.DocView.as_view(), name='doc-generic'),
    url(r'^view.+$', equipment_views.DocView.as_view(), name='doc'),
    url(r'^desc/$', equipment_views.DescView.as_view(), name='desc'),
    url(r'^contribute/$', equipment_views.ContributeView.as_view(), name='contribute'),

    url(r'^facilities/$', equipment_views.FacilityListView.as_view(), name='facilities'),

    url(r'^browse/(?:(?P<notation>[a-z\-\d\/]+)/)?$', equipment_views.BrowseView.as_view(), name='browse'),

    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^webauth/', include('django_webauth.urls', 'webauth')),
    url(r'^accounts/', include('dataox.auth.registration_urls')),

    url(r'^$', misc_views.SimpleView.as_view(template_name="equipment/index"), name='index'),
    url(r'^about/$', misc_views.SimpleView.as_view(template_name="equipment/about"), name='about'),
    url(r'^contact/$', misc_views.SimpleView.as_view(template_name="equipment/contact"), name='contact'),
    url(r'^legal-and-privacy/$', misc_views.SimpleView.as_view(template_name='legal'), name='legal'),
    
) + staticfiles_urlpatterns()
