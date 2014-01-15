from django.conf.urls import patterns

from . import views

urlpatterns = patterns('',
    (r'^$', views.IndexView.as_view(), {}, 'index'),
    (r'^vacancies/$', views.VacancyIndexView.as_view(), {}, 'vacancies-index'),
    # Units
    (r'^vacancies/(?P<oxpoints_id>\d{8})(?:\.(?P<format>[\da-z\-]+))?$', views.VacancyView.as_view(), {}, 'vacancies'),
    # Everything
    (r'^vacancies/all(?:\.(?P<format>[\da-z]+))?$', views.VacancyView.as_view(), {}, 'vacancies-all'),
    # Unit and subunits
    (r'^all-vacancies/(?P<oxpoints_id>\d{8})(?:\.(?P<format>[\da-z\-]+))?$', views.VacancyView.as_view(all=True), {}, 'all-vacancies'),
)
