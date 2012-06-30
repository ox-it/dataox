# -*- coding: utf-8 -*-
from lxml import etree
import locale
import rdflib

from django.conf import settings
from humfrey.utils.namespaces import NS

class Vacancy(object):
    def __init__(self, vacancy_id):
        self.id = vacancy_id
        self.title = None
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if set(dir(self)) != set(dir(other)):
            return False
        for name in dir(self):
            if not name.startswith('_') and getattr(self, name) != getattr(other, name):
                return False
        return True
    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Vacancy %s: %r' % (self.id, self.title)

    def triples(self, base_uri):
        uri = rdflib.URIRef(base_uri + self.id)
        contact_uri = rdflib.URIRef(uri + '/contact')
        salary_uri = rdflib.URIRef(uri + '/salary')

        triples = [
            (uri, NS.rdf.type, NS.vacancy.Vacancy),
            (uri, NS.foaf.homepage, rdflib.URIRef(self.url)),
            (uri, NS.oo.contact, contact_uri),
            (uri, NS.vacancy.applicationOpeningDate, rdflib.Literal(self.created)),
            (uri, NS.vacancy.applicationClosingDate, rdflib.Literal(self.closes)),
            (uri, NS.vacancy.internalApplicationsOnly, rdflib.Literal(self.internal)),
            (uri, NS.rdfs.label, rdflib.Literal(self.title)),
        ]

        if self.contact:
            triples.append((contact_uri, NS.rdf.type, NS.foaf.Agent))
        if 'name' in self.contact:
            triples.append((contact_uri, NS.foaf.name, rdflib.Literal(self.contact['name'])))
        if 'email' in self.contact:
            triples.append((contact_uri, NS.v.email, rdflib.URIRef(self.contact['email'])))
        if 'phone' in self.contact:
            phone_uri = self.phone_uri
            triples += [(contact_uri, NS.v.tel, phone_uri),
                        (phone_uri, NS.rdf.type, NS.v.Voice),
                        (phone_uri, NS.rdf.value, rdflib.Literal(self.contact['phone']))]

        if self.description:
            triples += [
                (uri, NS.rdfs.comment, rdflib.Literal(self.description, datatype=NS.xtypes['Fragment-XHTML'])),
                (uri, NS.rdfs.comment, rdflib.Literal(self.plain_description)),
            ]
        for root in self.roots:
            triples.append((uri, NS.oo.formalOrganization, root))
        for orgpart in self.orgparts:
            triples.append((uri, NS.oo.organizationalUnit, orgpart))

        for file in self.files:
            file_uri = rdflib.URIRef(file['local_url'])
            triples += [
                (uri, NS.foaf.page, file_uri),
                (uri, NS.vacancy.furtherParticulars, file_uri),
                (file_uri, NS.rdf.type, NS.foaf.Document),
                (file_uri, NS.dc['format'], rdflib.Literal(file['mimetype'])),
                (file_uri, NS.dcterms['title'], rdflib.Literal(file['title'])),
            ]
            if file.get('text'):
                triples.append((file_uri, NS.rdf.value, rdflib.Literal(file['text'], datatype=NS.xtypes['Fragment-PlainText'])))

        if self.salary:
            locale_code = settings.LANGUAGE_CODE
            locale.setlocale(locale.LC_ALL, ('%s_%s' % (locale_code[:2].lower(), locale_code[3:].upper()), 'UTF8'))
            label = u'Grade %s' % self.salary['grade']
            if self.salary.get('lower'):
                label += u': £' + locale.format('%d', self.salary['lower'], grouping=True)
                triples.append((salary_uri, NS.gr.hasMinCurrencyValue, rdflib.Literal(self.salary['lower'])))
                if self.salary.get('upper') and self.salary['lower'] != self.salary['upper']:
                    label += u' to £' + locale.format('%d', self.salary['upper'], grouping=True)
                if self.salary.get('discretionary'):
                    label += u', with discretionary range to £' + locale.format('%d', self.salary['discretionary'], grouping=True)
            if self.salary.get('upper'):
                triples.append((salary_uri, NS.gr.hasMaxCurrencyValue, rdflib.Literal(self.salary.get('discretionary') or self.salary['upper'])))
                if self.salary['upper'] == self.salary.get('lower'):
                    triples.append((salary_uri, NS.gr.hasCurrencyValue, rdflib.Literal(self.salary['upper'])))

            triples += [
                (uri, NS.vacancy.salary, salary_uri),
                (salary_uri, NS.rdf.type, NS.gr.UnitPriceSpecification),
                (salary_uri, NS.rdfs.label, rdflib.Literal(label)),
                (salary_uri, NS.gr.validThrough, rdflib.Literal(self.closes)),
                (salary_uri, NS.gr.hasCurrency, rdflib.Literal('GBP')),
            ]

        return triples

    @property
    def phone_uri(self):
        phone = self.contact['phone']
        if phone.startswith('0'):
            phone = '+44' + phone[1:]
        phone = ''.join(d for d in phone if d.isdigit() or d == '+')
        return rdflib.URIRef('tel:' + phone)

    @property
    def plain_description(self):
        return self.flatten(etree.fromstring(self.description)).strip()

    def _flatten(self, elem):
        if elem.tag == 'br':
            yield '\n'
            yield (elem.tail or '').strip()
        else:
            yield (elem.text or '').strip()
            for child in elem:
                for text in self._flatten(child):
                    yield text
            yield (elem.tail or '').strip()
    def flatten(self, elem):
        return ''.join(self._flatten(elem))
