from django.conf import settings

__all__ = ['base_template_chooser', 'maintenance_mode']

_base_templates = {'data': 'hosts/dataox.html',
                   'backstage': 'hosts/backstage.html',
                   'course': 'hosts/course.html',
                   'equipment': 'hosts/equipment.html',
                   'empty': 'hosts/dataox.html'}
_service_names = {'data': 'the Open Data Service',
                  'equipment': 'the Research Facilities database'}
_default_template = _base_templates['data']
_default_service_name = _service_names['data']

def base_template_chooser(request):
    host = request.host.name
    base_template_name = _base_templates.get(host, _default_template)
    return {'base_template_name': base_template_name,
            'host': host,
            'service_name': _service_names.get(host, _default_service_name)}

def maintenance_mode(request):
    return {'maintenance_mode': settings.MAINTENANCE_MODE}