from xml.sax.saxutils import escape, quoteattr
from django.utils.safestring import mark_safe

import rdflib

from humfrey.linkeddata.resource import BaseResource

class Account(object):
    _WIDGET_TEMPLATES = {
#        rdflib.URIRef('https://www.twitter.com/'): 'widgets/twitter.html',
    }

    _SERVICES = {
        'https://www.twitter.com/' : {'label': 'Twitter', 'icon': 'fa-twitter', 'prefix': '@'},
        'https://github.com/' : {'label': 'GitHub', 'icon': 'fa-github'},
        'https://www.facebook.com/' : {'label': 'Facebook', 'icon': 'fa-facebook'},
        'https://plus.google.com/' : {'label': 'Google+', 'icon': 'fa-google-plus', 'prefix': '+'},
        'http://www.skype.com/' : {'label': 'Skype', 'icon': 'fa-skype'},
        'http://www.youtube.com/' : {'label': 'YouTube', 'icon': 'fa-youtube'},
        'http://www.flickr.com/' : {'label': 'Flickr', 'icon': 'fa-flickr'},
        'http://www.linkedin.com/' : {'label': 'LinkedIn', 'icon': 'fa-linkedin'},
        'https://nexus.ox.ac.uk/' : {'label': 'Nexus', 'icon': 'fa-calendar'},
        'http://status.ox.ac.uk/' : {'label': 'System Status', 'icon': 'fa-tachometer'},
    }

    rdf_types = ('foaf:OnlineAccount',)

    def render(self):
        icon, service_homepage, service_label, account_name = None, None, None, None
        prefix = ''

        if self.foaf_accountName:
            account_name = self.foaf_accountName

        if isinstance(self.foaf_accountServiceHomepage, BaseResource):
            service_homepage = self.foaf_accountServiceHomepage.uri
            service = self._SERVICES.get(service_homepage, {})
            icon, service_label = service.get('icon'), service.get('label', service_homepage)
            prefix = service.get('prefix', '')
            if icon:
                icon = '<i class="fa {0}"></i> '.format(icon)

        rendered = ['<a href={0}'.format(quoteattr(self.uri))]
        if account_name and service_label:
            rendered.append(' title=')
            rendered.append(quoteattr(' {0} on {1}'.format(account_name, service_label)))
        rendered.append('>')
        rendered.append(icon or '')
        rendered.append(prefix)
        rendered.append(escape(account_name or self.uri))
        rendered.append('</a>')

        return mark_safe(''.join(rendered))

    def widget_templates(self):
        widgets = super(Account, self).widget_templates()
        service_homepage = self.foaf_accountServiceHomepage._identifier
        if service_homepage in self._WIDGET_TEMPLATES:
            widgets.append((self._WIDGET_TEMPLATES[service_homepage], self))
        return widgets
