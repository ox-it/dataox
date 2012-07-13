from django.conf.urls.defaults import url, include, patterns

from humfrey.misc import views as misc_views

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name="maps/index"), name='index'),
)
