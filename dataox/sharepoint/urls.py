from django.conf.urls import url

from . import views

app_name = 'sharepoint'

urlpatterns = [
    url(r'^user-profile-image/(?P<username>(?:ad-oak_)?[a-z\d]{1,8})/(?P<size>[a-z]+)/',
        views.UserProfileImageView.as_view(), name='user-profile-image'),
]
