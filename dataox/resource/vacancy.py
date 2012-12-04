import datetime

import dateutil.parser
from humfrey.linkeddata.resource import BaseResource
from humfrey.utils.namespaces import NS
import rdflib
import pytz

class Vacancy(object):
    types = ('vacancy:Vacancy',)
    search_item_template_name = 'vacancy/search_item'
    template_name = 'doc/vacancy'

    def is_closed(self):
        now = pytz.utc.localize(datetime.datetime.utcnow())
        if self.closes and self.closes < now:
                return True
        if self.opens and self.opens > now:
                return True
        return False

    @property
    def opens(self):
        opens = self.get('vacancy:applicationOpeningDate')
        if isinstance(opens, rdflib.Literal) and opens.datatype == NS.xsd.dateTime:
            return dateutil.parser.parse(opens)
    @property
    def closes(self):
        closes = self.get('vacancy:applicationClosingDate')
        if isinstance(closes, rdflib.Literal) and closes.datatype == NS.xsd.dateTime:
            return dateutil.parser.parse(closes)


    def get_json(self):
        html_description, text_description = None, None
        for comment in self.all.rdfs_comment:
            if comment.datatype in (NS.xtypes['Fragment-XHTML'], NS.xtypes['Fragment-HTML']):
                html_description = unicode(comment)
            else:
                text_description = unicode(comment)
        vacancy = {'label': self.label,
                   'id': self.get_with_datatype(NS.skos.notation, NS.oxnotation.vacancy),
                   'uri': self.uri,
                   'url': self.doc_url,
                   'webpage': self.foaf_homepage,
                   'opens': self.vacancy_applicationOpeningDate,
                   'closes': self.vacancy_applicationClosingDate,
                   'location': self.dc_spatial,
                   'html_description': html_description,
                   'text_description': text_description}

        salary = self.vacancy_salary
        if salary:
            vacancy['salary'] = {'lower': salary.gr_hasMinCurrencyValue,
                                 'upper': salary.gr_hasMaxCurrencyValue,
                                 'currency': salary.gr_hasCurrency,
                                 'label': salary.label}

        contact = self.oo_contact
        if isinstance(contact, BaseResource):
            vacancy['contact'] = {'label': contact.label}
            if isinstance(contact.v_email, BaseResource):
                vacancy['contact']['email'] = contact.v_email.uri.replace('mailto:', '', 1)
            if isinstance(contact.v_tel, BaseResource):
                vacancy['contact']['phone'] = contact.v_tel.label

        related = (('formalOrganization', 'oo:formalOrganization'),
                   ('organizationPart', 'oo:organizationPart'),
                   ('basedNear', 'foaf:based_near'))
        for key, predicate in related:
            for obj in self.get_all(predicate):
                data = {'label': obj.label,
                        'uri': obj.uri,
                        'url': obj.doc_url,
                        'webpage': obj.foaf_homepage}
                adr = obj.get('v:adr')
                if adr:
                    data['address'] = {'streetAddress': adr.get('v:street-address'),
                                       'extendedtAddress': adr.get('v:extended-address'),
                                       'locality': adr.get('v:locality'),
                                       'postalCode': adr.get('v:postal-code')}
                if obj.get('geo:lat') and obj.get('geo:long'):
                    data['location'] = {'lat': obj.get('geo:lat'),
                                        'long': obj.get('geo:long')}

                if key not in vacancy:
                    vacancy[key] = []
                vacancy[key].append(data)

        return vacancy