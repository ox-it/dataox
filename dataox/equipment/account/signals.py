from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .forms import SignupForm

@receiver(user_logged_in)
def ouh_user_group(sender, request, user, **kwargs):
    domain = user.email.rsplit('@', 1)[-1]
    ouh_group, _ = Group.objects.get_or_create(name='ouh')
    if domain in SignupForm.good_domains:
        user.groups.add(ouh_group)
    else:
        user.groups.remove(ouh_group)
