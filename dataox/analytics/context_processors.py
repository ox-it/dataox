analytics_ids = {'equipment': 'UA-32168758-1'}

def do_not_track(request):
    analytics_id = analytics_ids.get(request.host.name)
    request.using_analytics = analytics_id is not None
    return {'do_not_track': request.META.get('HTTP_DNT') == '1',
            'analytics_id': analytics_id,
            'analytics_enabled': analytics_id is not None}
