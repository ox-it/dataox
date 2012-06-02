from xml.sax.saxutils import escape, quoteattr
from django.utils.safestring import mark_safe

import rdflib

class Account(object):
    _WIDGET_TEMPLATES = {
        rdflib.URIRef('http://www.twitter.com/'): 'widgets/twitter.html',
    }

    rdf_types = ('foaf:OnlineAccount',)

    def render(self):
        if self.foaf_accountServiceHomepage._identifier == rdflib.URIRef('http://www.twitter.com/'):
            return mark_safe('<a href="%s"><img class="icon" src="http://twitter-badges.s3.amazonaws.com/t_mini-b.png" alt="%s on Twitter"/> @%s</a>' % tuple(map(escape,
                (self.foaf_accountProfilePage.uri, self.foaf_accountName, self.foaf_accountName))))
        else:
            return mark_safe('<a href="%s">%s at %s</a>' % tuple(map(escape, (self.foaf_accountProfilePage.uri, self.foaf_accountName, self.foaf_accountServiceHomepage.uri))))

    def widget_templates(self):
        widgets = super(Account, self).widget_templates()
        service_homepage = self.foaf_accountServiceHomepage._identifier
        if service_homepage in self._WIDGET_TEMPLATES:
            widgets.append((self._WIDGET_TEMPLATES[service_homepage], self))
        return widgets