import datetime
import json

import dateutil.parser
from humfrey.linkeddata.resource import BaseResource
from humfrey.utils.namespaces import NS
from lxml.builder import E
import lxml.etree
import rdflib
import pytz

from django.http import HttpResponse
from django_conneg.decorators import renderer

def xhtml_to_html(xml, serialize=True):
    xml = lxml.etree.fromstring(xml)
    xhtml_ns = '{http://www.w3.org/1999/xhtml}'
    def walk(e):
        if e.tag.startswith(xhtml_ns):
            e.tag = e.tag[len(xhtml_ns):]
        for c in e:
            walk(c)
    walk(xml)
    html = lxml.etree.Element(xml.tag)
    html.text, html.tail = xml.text, xml.tail
    html.extend(xml)
    if serialize:
        return lxml.etree.tostring(html, method='html').decode('utf-8')
    else:
        return html

class Vacancy(object):
    types = ('vacancy:Vacancy',)
    #search_item_template_name = 'vacancy/search_item'
    template_name = 'doc/vacancy'

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(uri)s oo:formalOrganization %(formalOrganization)s',
            '%(uri)s oo:organizationPart %(organizationPart)s',
            '%(uri)s foaf:based_near %(basedNear)s',
            '%(uri)s vacancy:salary %(salary)s',
            '%(uri)s oo:contact %(contact)s',
            '%(uri)s vacancy:furtherParticulars %(furtherParticulars)s',
        ]

    related = (('organizationPart', 'oo:organizationPart'),
               ('formalOrganization', 'oo:formalOrganization'),
               ('basedNear', 'foaf:based_near'))

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

    @property
    def id(self):
        return self.get_with_datatype(NS.skos.notation, NS.oxnotation.vacancy)

    def get_json(self):
        html_description, text_description = None, None
        for comment in self.all.rdfs_comment:
            if comment.datatype in (NS.xtypes['Fragment-XHTML'], NS.xtypes['Fragment-HTML']):
                html_description = str(comment)
            else:
                text_description = str(comment)
        vacancy = {'label': self.label,
                   'id': self.id,
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
            vacancy['contact'] = {}
            if contact.actual_label:
                vacancy['contact']['label'] = contact.actual_label
            if isinstance(contact.v_email, BaseResource):
                vacancy['contact']['email'] = contact.v_email.uri.replace('mailto:', '', 1)
            if isinstance(contact.v_tel, BaseResource):
                vacancy['contact']['phone'] = contact.v_tel.label

        for key, predicate in self.related:
            for obj in self.get_all(predicate):
                data = {'label': obj.label,
                        'uri': obj.uri,
                        'url': obj.doc_url,
                        'webpage': obj.foaf_homepage,
                        'logo': obj.foaf_logo}
                adr = obj.get('v:adr')
                if adr:
                    data['address'] = {'streetAddress': adr.get('v:street-address'),
                                       'extendedAddress': adr.get('v:extended-address'),
                                       'locality': adr.get('v:locality'),
                                       'postalCode': adr.get('v:postal-code')}
                if obj.get('geo:lat') and obj.get('geo:long'):
                    data['location'] = {'lat': obj.get('geo:lat'),
                                        'long': obj.get('geo:long')}

                if key not in vacancy:
                    vacancy[key] = []
                vacancy[key].append(data)

        return vacancy

    def get_xml(self):
        vacancy = E('vacancy',
            E('uri', self.uri),
            E('url', self.doc_url),
            id=self.id)
        if self.foaf_homepage:
            vacancy.append(E('webpage', self.foaf_homepage.uri))
        if self.actual_label:
            vacancy.append(E('label', str(self.actual_label)))
        if self.opens:
            vacancy.append(E('opens', self.opens.isoformat()))
        if self.closes:
            vacancy.append(E('closes', self.closes.isoformat()))
        if self.dc_spatial:
            vacancy.append(E('location', str(self.dc_spatial)))
        for comment in self.all.rdfs_comment:
            if comment.datatype == NS.xtypes['Fragment-XHTML']:
                vacancy.append(E('description',
                                 lxml.etree.fromstring(comment),
                                 media_type='application/xhtml+xml',
                                 ))
                html_comment = xhtml_to_html(comment)
                vacancy.append(E('description',
                                 html_comment,
                                 format='application/xhtml+xml',
                                 media_type='text/html'))
            elif comment.datatype == NS.xtypes['Fragment-HTML']:
                comment = lxml.etree.fromstring(comment, parser=lxml.etree.HTMLParser())
                comment = comment.xpath('/html/body/div')[0]
                vacancy.append(E('description',
                                 lxml.etree.tostring(comment, method='html'),
                                 media_type='text/html',
                                 format='application/xhtml+xml'))
                comment.attrib['xmlns'] = 'http://www.w3.org/1999/xhtml'
                vacancy.append(E('description',
                                 comment,
                                 media_type='application/xhtml+xml'))
            else:
                vacancy.append(E('description',
                                 str(comment),
                                 media_type='text/plain',
                                 format='text/plain'))
        for key, predicate in self.related:
            related = self.get(predicate)
            if not related:
                continue
            sub = E(key,
                E('uri', related.uri),
                E('url', related.doc_url))
            if related.foaf_homepage:
                sub.append(E('webpage', related.foaf_homepage.uri))
            if related.foaf_logo:
                sub.append(E('logo', related.foaf_logo.uri))
            if related.actual_label:
                sub.append(E('label', str(related.actual_label)))
            if related.v_adr:
                address = E('address')
                for p, n in [('v:extended-address', 'extended-address'),
                             ('v:street-address', 'street-address'),
                             ('v:locality', 'locality'),
                             ('v:postal-code', 'postal-code'),
                             ('v:country-name', 'country')]:
                    if related.v_adr.get(p):
                        address.append(E(n, str(related.v_adr.get(p))))
                sub.append(address)
            if related.geo_lat and related.geo_long:
                sub.append(E('location',
                    E('lat', str(related.geo_lat)),
                    E('long', str(related.geo_long))))
            vacancy.append(sub)

        salary = self.vacancy_salary
        if isinstance(salary, BaseResource):
            salary_elem = E('salary')
            if salary.rdfs_label:
                salary_elem.append(E('label', str(salary.rdfs_label)))
            if salary.gr_hasMinCurrencyValue:
                salary_elem.append(E('lower', str(salary.gr_hasMinCurrencyValue)))
            if salary.gr_hasMinCurrencyValue:
                salary_elem.append(E('upper', str(salary.gr_hasMaxCurrencyValue)))
            if salary.gr_hasCurrency:
                salary_elem.append(E('currency', str(salary.gr_hasCurrency)))
            vacancy.append(salary_elem)

        contact = self.oo_contact
        if isinstance(contact, BaseResource):
            contact_elem = E('contact')
            if contact.actual_label:
                contact_elem.append(E('label', str(contact.actual_label)))
            if isinstance(contact.v_email, BaseResource):
                contact_elem.append(E('email', contact.v_email.uri.replace('mailto:', '', 1)))
            if isinstance(contact.v_tel, BaseResource):
                contact_elem.append(E('phone', str(contact.v_tel.label)))
            vacancy.append(contact_elem)

        document_urls = E('document_urls')
        for document in self.all.vacancy_furtherParticulars:
            document_urls.append(E('document_url', document.uri))
        if len(document_urls):
            vacancy.append(document_urls)
        return vacancy

    def get_naturejobs_xml(self):
        organization_part = self.get('oo:organizationPart')
        formal_organization = self.get('oo:formalOrganization')
        based_near = self.get('foaf:based_near')

        employer_name = ', '.join([org.actual_label for org in [organization_part,
                                                                formal_organization]
                                   if org]) or 'University of Oxford'

        try:
            employer_url = (organization_part or formal_organization).get('foaf:homepage').uri
        except AttributeError:
            employer_url = 'http://www.ox.ac.uk/'

        job = E('job',
            E('requisition-number', str(self.id)),
            E('employer-name', employer_name),
            E('employer-url', employer_url),
        )
        if self.foaf_homepage:
            job.append(E('application-url', self.foaf_homepage.uri))

        for comment in self.all.rdfs_comment:
            if comment.datatype == NS.xtypes['Fragment-XHTML']:
                html_comment = xhtml_to_html(comment, serialize=False)
                break
        else:
            html_comment = lxml.etree.fromstring('<div><p>No description available.</p></div>')
        try:
            salary = self.get('vacancy:salary').actual_label
        except AttributeError:
            pass
        else:
            if salary is not None:
                salary = E('p', E('em', "Salary: " + str(salary)))
                html_comment.text, salary.tail = None, html_comment.text
                html_comment.insert(0, salary)

        job.append(E('description',
                     lxml.etree.tostring(html_comment, method='html').decode()))

        if self.actual_label:
            job.append(E('title', str(self.actual_label)))
        if self.opens:
            job.append(E('created-on', self.opens.strftime('%Y-%m-%d')))
        if self.closes:
            job.append(E('expires-on', self.closes.strftime('%Y-%m-%d')))

        try:
            adr = (based_near or organization_part or formal_organization).get('v:adr')
        except AttributeError:
            adr = None

        address_data = {}
        if adr:
            for p, n in [('v:extended-address', 'address-line-1'),
                         ('v:street-address', 'address-line-2'),
                         ('v:locality', 'city'),
                         ('v:postal-code', 'postal-code'),
                         ('v:country-name', 'country')]:
                if adr.get(p):
                    address_data[n] = str(adr.get(p))
        if 'city' not in address_data:
            address_data['city'] = 'Oxford'
        if 'country' not in address_data:
            address_data['country'] = 'United Kingdom'
        if 'address-line-2' in address_data and 'address-line-1' not in address_data:
            address_data['address-line-1'] = address_data.pop('address-line-2')

        address = E('address')
        for n in ['address-line-1', 'address-line-2', 'city', 'postal-code', 'country']:
            if n in address_data:
                address.append(E(n, address_data[n]))
        job.append(address)

        return job

    def get_naturecareers_xml(self):
        organization_part = self.get('oo:organizationPart')
        formal_organization = self.get('oo:formalOrganization')
        based_near = self.get('foaf:based_near')

        employer_name = ', '.join([org.actual_label for org in [organization_part,
                                                                formal_organization]
                                   if org]) or 'University of Oxford'

        try:
            employer_url = (organization_part or formal_organization).get('foaf:homepage').uri
        except AttributeError:
            employer_url = 'http://www.ox.ac.uk/'

        job = E('job',
            E('requisitionNumber', str(self.id)),
            E('referenceId', str(self.id)),
            E('employerName', employer_name),
            E('employerUrl', employer_url),
        )
        if self.foaf_homepage:
            job.append(E('applicationUrl', self.foaf_homepage.uri))

        for comment in self.all.rdfs_comment:
            if comment.datatype == NS.xtypes['Fragment-XHTML']:
                html_comment = xhtml_to_html(comment, serialize=False)
                break
        else:
            html_comment = lxml.etree.fromstring('<div><p>No description available.</p></div>')
        try:
            salary = self.get('vacancy:salary').actual_label
        except AttributeError:
            pass
        else:
            if salary is not None:
                salary = E('p', E('em', "Salary: " + str(salary)))
                html_comment.text, salary.tail = None, html_comment.text
                html_comment.insert(0, salary)

        description = E('description')
        description.text = lxml.etree.CDATA(lxml.etree.tostring(html_comment, method='html'))
        job.append(description)

        if self.actual_label:
            job.append(E('title', str(self.actual_label)))
        if self.opens:
            job.append(E('createdOn', self.opens.strftime('%Y-%m-%d')))
        if self.closes:
            job.append(E('expiresOn', self.closes.strftime('%Y-%m-%d')))

        try:
            adr = (based_near or organization_part or formal_organization).get('v:adr')
        except AttributeError:
            adr = None

        address_data = {}
        if adr:
            for p, n in [('v:extended-address', 'addressLine1'),
                         ('v:street-address', 'addressLine2'),
                         ('v:locality', 'city'),
                         ('v:postal-code', 'postalCode'),
                         ('v:country-name', 'country')]:
                if adr.get(p):
                    address_data[n] = str(adr.get(p))
        if 'city' not in address_data:
            address_data['city'] = 'Oxford'
        if 'country' not in address_data:
            address_data['country'] = 'United Kingdom'
        if 'addressLine2' in address_data and 'addressLine1' not in address_data:
            address_data['addressLine1'] = address_data.pop('addressLine2')

        address = E('address')
        for n in ['addressLine1', 'addressLine2', 'city', 'postalCode', 'country']:
            if n in address_data:
                address.append(E(n, address_data[n]))
        job.append(address)

        return job

    @renderer(format='json', mimetypes=('application/json',), name='JSON')
    def render_json(self, request, context, template_name):
        return HttpResponse(json.dumps(self.get_json(), indent=2),
                            content_type='application/json')

    @renderer(format='xml', mimetypes=('application/xml',), name='XML')
    def render_xml(self, request, context, template_name):
        return HttpResponse(lxml.etree.tostring(self.get_xml(), pretty_print=True),
                            content_type='application/xml')

    @renderer(format='naturejobs-xml', mimetypes=('x-application/naturejobs+xml',), name='NatureJobs XML')
    def render_naturejobs_xml(self, request, context, template_name):
        return HttpResponse(lxml.etree.tostring(self.get_naturejobs_xml(), pretty_print=True),
                            content_type='application/xml')
