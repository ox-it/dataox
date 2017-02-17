from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dataox.core import views as core_views

from .main import handler404, handler500

urlpatterns = [
    url(r'^$', handler404, name='index'),
] + staticfiles_urlpatterns()

handler503 = core_views.MaintenanceModeView.as_view()
