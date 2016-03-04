from django.conf.urls import url, patterns

from . import views

urlpatterns = patterns('',
    url(r'^user-profile-image/(?P<username>(?:ad-oak_)?[a-z\d]{1,8})/(?P<size>[a-z]+)/',
        views.UserProfileImageView.as_view(), name='user-profile-image'),
)