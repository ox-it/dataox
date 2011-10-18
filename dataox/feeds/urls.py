from django.conf.urls.defaults import patterns

from dataox.feeds import views

urlpatterns = patterns('',
    (r'^$', views.IndexView.as_view(), {}, 'index'),
    (r'^vacancies/$', views.VacancyIndexView.as_view(), {}, 'vacancies-index'),
    (r'^vacancies/(?P<oxpoints_id>\d{8})(?:\.(?P<format>[\da-z]+))?$', views.VacancyView.as_view(), {}, 'vacancies'),
    (r'^all-vacancies/(?P<oxpoints_id>\d{8})(?:\.(?P<format>[\da-z]+))?$', views.VacancyView.as_view(all=True), {}, 'all-vacancies'),
)