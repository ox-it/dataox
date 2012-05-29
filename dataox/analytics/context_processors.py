analytics_ids = {'equipment': 'UA-32168758-1'}

def do_not_track(request):
    analytics_id = analytics_ids.get(request.host.name)
    return {'do_not_track': 'true' if request.META.get('HTTP_DNT') == '1' else 'false',
            'analytics_id': analytics_id,
            'analytics_enabled': analytics_id is not None}
