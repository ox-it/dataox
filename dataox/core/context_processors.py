__all__ = ['base_template_chooser']

_base_templates = {'data': 'hosts/dataox.html',
                   'backstage': 'hosts/backstage.html',
                   'timeseries': 'hosts/timeseries.html',
                   'course': 'hosts/course.html',
                   'equipment': 'hosts/equipment.html',
                   'empty': 'hosts/dataox.html'}
_default_template = _base_templates['data']

def base_template_chooser(request):
    host = request.host.name
    base_template_name = _base_templates.get(host, _default_template)
    return {'base_template_name': base_template_name}
