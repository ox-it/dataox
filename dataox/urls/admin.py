from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from humfrey.manage import views as manage_views
from humfrey.misc import views as misc_views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', misc_views.AuthenticatedSimpleView.as_view(template_name='manage/index'), name='index'),
    url(r'^pingback/', include('humfrey.pingback.urls.admin', 'pingback')),
    url(r'^update/', include('humfrey.update.urls', 'update')),
    url(r'^login/', manage_views.LoginView.as_view(), name='login'),
    url(r'^logout/', manage_views.LogoutView.as_view(), name='logout'),
    url(r'^webauth/', include('django_webauth.urls', 'webauth')),
    url(r'^admin/', admin.site.urls),
)

handler404 = misc_views.SimpleView.as_view(template_name='404-empty', context={'status_code':404})
handler500 = misc_views.SimpleView.as_view(template_name='500', context={'status_code':500})
