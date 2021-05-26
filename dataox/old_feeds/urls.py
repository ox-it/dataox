from django.conf.urls import url

from . import views

app_name = 'old-feeds'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^vacancies/$', views.VacancyIndexView.as_view(), name='vacancies-index'),
    # Units
    url(r'^vacancies/(?P<oxpoints_id>\d{8})(?:\.(?P<format>[\da-z\-]+))?$', views.VacancyView.as_view(), name='vacancies'),
    # Everything
    url(r'^vacancies/(?P<feed_name>[a-z\-]+)(?:\.(?P<format>[\da-z\-]+))?$', views.VacancyView.as_view(), name='vacancies-named-feed'),
    # Unit and subunits
    url(r'^all-vacancies/(?P<oxpoints_id>\d{8})(?:\.(?P<format>[\da-z\-]+))?$', views.VacancyView.as_view(all=True), name='all-vacancies'),
]
