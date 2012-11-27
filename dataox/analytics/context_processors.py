"""
Context processor for controlling Google Analytics in the template.

We use the IT Services "optional analytics" JavaScript documented at
http://infodev.oucs.ox.ac.uk/analytics/.
"""

from django_hosts import reverse_full

# hostname will be used with the _setDomainName Google Analytics option; see:
# <https://developers.google.com/analytics/devguides/collection/gajs/methods/gaJSApiDomainDirectory#_gat.GA_Tracker_._setDomainName>
# login_possible determines whether users will be told that the policy will
# become opt-out if they log in.
analytics_meta = [{'analytics_id': 'UA-32168758-1',
                   'hosts': ('equipment',),
                   'hostname': 'www.research-facilities.ox.ac.uk',
                   'login_possible': True,
                   'privacy_policy_url': reverse_full('equipment', 'legal') + '#analytics'},
                  {'analytics_id': 'UA-35258720-1',
                   'hosts': ('data', 'course', 'timeseries', 'empty'),
                   'hostname': '.data.ox.ac.uk',
                   'login_possible': False,
                   'privacy_policy_url': reverse_full('data', 'legal') + '#analytics'}]

analytics_meta_by_host = dict((host, meta) for meta in analytics_meta
                                           for host in meta['hosts'])

def do_not_track(request):
    meta = analytics_meta_by_host.get(request.host.name)
    if meta:
        request.using_analytics = True
        return {'analytics': {'do_not_track': request.META.get('HTTP_DNT') == '1',
                              'id': meta['analytics_id'],
                              'hostname': meta['hostname'],
                              'login_possible': meta['login_possible'],
                              'privacy_policy_url': meta['privacy_policy_url']}}
    else:
        return {}
