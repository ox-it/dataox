from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import LoginView

import django_webauth.views

from humfrey.misc import views as misc_views

from dataox.equipment import views as equipment_views

from .main import handler404, handler500

urlpatterns = [
    url(r'^search/$', equipment_views.SearchView.as_view(), name='search'),

    url(r'^view/$', equipment_views.DocView.as_view(), name='doc-generic'),
    url(r'^view.+$', equipment_views.DocView.as_view(), name='doc'),
    url(r'^desc/$', equipment_views.DescView.as_view(), name='desc'),
    url(r'^contribute/$', equipment_views.ContributeView.as_view(), name='contribute'),

    url(r'^facilities/$', equipment_views.FacilityListView.as_view(), name='facilities'),
    url(r'^departments/$', equipment_views.LastIssuedView.as_view(), name='last-issued'),

    url(r'^browse/(?:(?P<notation>[a-z\-\d\/]+)/)?$', equipment_views.BrowseView.as_view(), name='browse'),

    url(r'^accounts/webauth/$', django_webauth.views.LoginView.as_view(), name='account_webauth'),
    url(r'^accounts/logout/$', django_webauth.views.LogoutView.as_view(), name="account_logout"),

    url(r'^shibboleth-login/', LoginView.as_view(redirect_authenticated_user=True), name='shibboleth-login'),

    url(r'^$', misc_views.SimpleView.as_view(template_name="equipment/index"), name='index'),
    url(r'^about/$', misc_views.SimpleView.as_view(template_name="equipment/about"), name='about'),
    url(r'^contact/$', misc_views.SimpleView.as_view(template_name="equipment/contact"), name='contact'),
    url(r'^legal-and-privacy/$', misc_views.SimpleView.as_view(template_name='legal'), name='legal'),
    
] + staticfiles_urlpatterns()
