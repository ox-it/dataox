from django.conf import settings
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django_hosts import reverse

from humfrey.desc import views as desc_views
from humfrey.misc import views as misc_views

from .main import handler500

class IdView(desc_views.IdView):
    @property
    def doc_view(self):
        return reverse('doc-generic', host=settings.DEFAULT_HOST)
    @property
    def desc_view(self):
        return reverse('desc', host=settings.DEFAULT_HOST)

urlpatterns = [
    url(r'^.*', IdView.as_view(), {}, 'id'),
] + staticfiles_urlpatterns()

handler404 = misc_views.SimpleView.as_view(template_name='404-id', context={'status_code':404})
