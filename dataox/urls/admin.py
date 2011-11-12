from django.conf.urls.defaults import patterns, include, url

from humfrey.misc import views as misc_views

urlpatterns = patterns('',
    url(r'^$', misc_views.AuthenticatedSimpleView.as_view(template_name='admin/index'), name='index'),
    url(r'^pingback/', include('humfrey.pingback.urls.admin', 'pingback')),
    url(r'^update/', include('humfrey.update.urls', 'update')),
    url(r'^login/', misc_views.LoginView.as_view(), name='login'),
    url(r'^logout/', misc_views.LogoutView.as_view(), name='logout'),
    url(r'^webauth/', include('django_webauth.urls', 'webauth')),
)

handler404 = misc_views.SimpleView.as_view(template_name='404-empty', context={'status_code':404})
handler500 = misc_views.SimpleView.as_view(template_name='500', context={'status_code':500})
