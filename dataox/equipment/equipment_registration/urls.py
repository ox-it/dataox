from django.conf.urls.defaults import patterns, url, include

from django.views.generic.simple import direct_to_template
from registration.views import activate, register

from .forms import RegistrationForm

backend = 'dataox.equipment.equipment_registration.backends.EquipmentBackend'

urlpatterns = patterns('',
                       url(r'^activate/complete/$',
                           direct_to_template,
                           {'template': 'equipment/registration/activation_complete.html'},
                           name='registration_activation_complete'),
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "invalid key" message instead of a
                       # confusing 404.
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           activate,
                           {'backend': backend},
                           name='registration_activate'),
                       url(r'^register/$',
                           register,
                           {'backend': backend,
                            'form_class': RegistrationForm},
                           name='registration_register'),
                       url(r'^register/complete/$',
                           direct_to_template,
                           {'template': 'equipment/registration/registration_complete.html'},
                           name='registration_complete'),
                       url(r'^register/closed/$',
                           direct_to_template,
                           {'template': 'equipment/registration/registration_closed.html'},
                           name='registration_disallowed'),
                       (r'', include('registration.auth_urls')),
                       )
