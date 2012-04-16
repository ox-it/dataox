from django.conf.urls.defaults import url, patterns

from . import views
from humfrey.misc import views as misc_views

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='course/index'), name='index'),
)