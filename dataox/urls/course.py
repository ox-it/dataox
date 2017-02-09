from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views

from .main import handler404, handler500

urlpatterns = [
    url(r'^', include('dataox.course.urls')),
] + staticfiles_urlpatterns()
