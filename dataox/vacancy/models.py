# -*- coding: utf-8 -*-

import datetime
import locale
import logging
import re

import dateutil.parser
from lxml import etree
import pytz
import rdflib

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.db import models
from humfrey.elasticsearch.query import ElasticSearchEndpoint
from humfrey.utils.namespaces import NS

logger = logging.getLogger(__name__)
email_re = re.compile(r'(?P<localpart>[a-zA-Z\d\-._]+)@(?P<host>[a-zA-Z\d\-.]+)')

class Vacancy(DirtyFieldsMixin, models.Model):
    vacancy_id = models.CharField(max_length=10)
    title = models.CharField(max_length=512)

    location = models.CharField(max_length=1024)
    organizationPart = models.CharField(max_length=256, blank=True)
    formalOrganization = models.CharField(max_length=256, blank=True)
    basedNear = models.CharField(max_length=256, blank=True)
    
    description = models.TextField()
    
    salary = models.CharField(max_length=512, blank=True)
    salary_grade = models.CharField(max_length=32, blank=True)
    salary_lower = models.PositiveIntegerField(null=True, blank=True)
    salary_upper = models.PositiveIntegerField(null=True, blank=True)
    salary_discretionary = models.PositiveIntegerField(null=True, blank=True)

    contact_name = models.CharField(max_length=128, blank=True)
    contact_email = models.CharField(max_length=128, blank=True)
    contact_phone = models.CharField(max_length=128, blank=True)
    
    url = models.URLField(max_length=2048, blank=True)
    apply_url = models.URLField(max_length=2048, blank=True)

    opening_date = models.CharField(max_length=25)
    closing_date = models.CharField(max_length=25, null=True, blank=True)

    internal = models.BooleanField()
    
    last_checked = models.DateTimeField(auto_now=True)

    @property
    def opening_date_dt(self):
        return dateutil.parser.parse(self.opening_date) if self.opening_date else None
    @property
    def closing_date_dt(self):
        return dateutil.parser.parse(self.closing_date) if self.closing_date else None
    
    def __unicode__(self):
        return u'{0}: {1}'.format(self.vacancy_id, self.title)

    def update_location_fields(self, store_slug):
        # Perform a query against ElasticSearch to find an organization for this location
        search_endpoint = ElasticSearchEndpoint(store_slug, 'organization')
        results = search_endpoint.query({'query': {'query_string': {'query': self.location.replace('-', ' ')}}})
        hits = results['hits']['hits']
        if hits:
            hit = hits[0]['_source']
            self.organizationPart = hit['uri']
            try:
                self.formalOrganization = hit['rootOrganization']['uri']
            except KeyError:
                pass
            logger.debug("Matched '%s' to organization '%s' (%s)", self.location, hit.get('label'), hit['uri'])
            site_uris = [site['uri'] for site in hit.get('site', [])]
        else:
            site_uris = []

        # And now find a location
        search_endpoint = ElasticSearchEndpoint(store_slug, 'spatial-thing')
        results = search_endpoint.query({'query': {'bool': {'must': {'query_string': {'query': self.location}},
                                                            'should': [{'terms': {'uri': site_uris}}]}}})
        hits = results['hits']['hits']
        if hits:
            hit = hits[0]['_source']
            logger.debug("Matched '%s' to spatial-thing '%s' (%s)", self.location, hit.get('label'), hit['uri'])
            self.basedNear = hit['uri']


    def triples(self, base_uri):
        uri = rdflib.URIRef(base_uri + self.vacancy_id)
        contact_uri = rdflib.URIRef(uri + '/contact')
        salary_uri = rdflib.URIRef(uri + '/salary')

        triples = [
            (uri, NS.rdf.type, NS.vacancy.Vacancy),
            (uri, NS.oo.contact, contact_uri),
            (uri, NS.vacancy.applicationOpeningDate, rdflib.Literal(self.opening_date, datatype=NS.xsd.dateTime)),
            (uri, NS.vacancy.internalApplicationsOnly, rdflib.Literal(self.internal)),
            (uri, NS.rdfs.label, rdflib.Literal(self.title)),
            (uri, NS.skos.notation, rdflib.Literal(self.vacancy_id, datatype=NS.oxnotation.vacancy)),
        ]
        
        if self.closing_date:
            triples.append((uri, NS.vacancy.applicationClosingDate, rdflib.Literal(self.closing_date, datatype=NS.xsd.dateTime)))

        # Only include a URL if the vacancy is still being advertised.
        if not self.closing_date or \
              self.closing_date_dt > pytz.utc.localize(datetime.datetime.utcnow()):
            triples.append((uri, NS.foaf.homepage, rdflib.URIRef(self.url)))


        if self.contact_name or self.contact_email or self.phone_uri:
            triples += [(uri, NS.oo.contact, contact_uri),
                        (contact_uri, NS.rdf.type, NS.foaf.Agent)]
        if self.contact_name:
            triples.append((contact_uri, NS.foaf.name, rdflib.Literal(self.contact_name)))
        # Sometimes we see more than one e-mail address in this field
        for localpart, host in email_re.findall(self.contact_email):
            triples.append((contact_uri, NS.v.email, rdflib.URIRef('mailto:{0}@{1}'.format(localpart, host.lower()))))
        if self.phone_uri:
            phone_uri = self.phone_uri
            triples += [(contact_uri, NS.v.tel, phone_uri),
                        (phone_uri, NS.rdf.type, NS.v.Voice),
                        (phone_uri, NS.rdf.value, rdflib.Literal(self.contact_phone))]

        if self.description:
            try:
                triples += [
                    (uri, NS.rdfs.comment, rdflib.Literal(self.description, datatype=NS.xtypes['Fragment-XHTML'])),
                    (uri, NS.rdfs.comment, rdflib.Literal(self.plain_description)),
                ]
            except Exception:
                logger.exception("Couldn't parse description for vacancy %s", self.vacancy_id)
        if self.location:
            triples.append((uri, NS.dc.spatial, rdflib.Literal(self.location)))
        for formalOrganization in self.formalOrganization.split():
            triples.append((uri, NS.oo.formalOrganization, rdflib.URIRef(formalOrganization)))
        for organizationPart in self.organizationPart.split():
            triples.append((uri, NS.oo.organizationPart, rdflib.URIRef(organizationPart)))
        for basedNear in self.basedNear.split():
            triples.append((uri, NS.foaf.based_near, rdflib.URIRef(basedNear)))

        for document in self.document_set.all():
            if not document.local_url:
                continue

            document_uri = rdflib.URIRef(document.local_url)
            triples += [
                (uri, NS.foaf.page, document_uri),
                (uri, NS.vacancy.furtherParticulars, document_uri),
                (document_uri, NS.rdf.type, NS.foaf.Document),
                (document_uri, NS.dc['format'], rdflib.Literal(document.mimetype)),
                (document_uri, NS.dcterms['title'], rdflib.Literal(document.title)),
            ]
            if document.text:
                triples.append((document_uri, NS.rdf.value, rdflib.Literal(document.text, datatype=NS.xtypes['Fragment-PlainText'])))

        if self.salary_grade:
            # This is no longer used, as we end up losing information.
            locale_code = settings.LANGUAGE_CODE
            locale.setlocale(locale.LC_ALL, ('%s_%s' % (locale_code[:2].lower(), locale_code[3:].upper()), 'UTF8'))
            label = u'Grade %s' % self.salary_grade
            if self.salary_lower:
                label += u': £' + locale.format('%d', self.salary_lower, grouping=True)
                triples.append((salary_uri, NS.gr.hasMinCurrencyValue, rdflib.Literal(self.salary_lower)))
                if self.salary_upper and self.salary_lower != self.salary_upper:
                    label += u' to £' + locale.format('%d', self.salary_upper, grouping=True)
                if self.salary_discretionary:
                    label += u', with discretionary range to £' + locale.format('%d', self.salary_discretionary, grouping=True)
            if self.salary_upper:
                triples.append((salary_uri, NS.gr.hasMaxCurrencyValue, rdflib.Literal(self.salary_discretionary or self.salary_upper)))
                if self.salary_upper == self.salary_lower:
                    triples.append((salary_uri, NS.gr.hasCurrencyValue, rdflib.Literal(self.salary_upper)))
            if self.salary_grade:
                triples.append((salary_uri, NS.adhoc.salaryGrade, rdflib.Literal(self.salary_grade)))

            # Our recruit.ox regex can only handle GBP anyway, so the first
            # two cases will currently never happen.
            if u'€' in self.salary:
                currency = 'EUR'
            elif u'$' in self.salary:
                currency = 'USD'
            else:
                currency = 'GBP'

            triples += [
                (uri, NS.vacancy.salary, salary_uri),
                (salary_uri, NS.rdf.type, NS.gr.UnitPriceSpecification),
                (salary_uri, NS.rdfs.label, rdflib.Literal(self.salary)),
                (salary_uri, NS.gr.hasCurrency, rdflib.Literal(currency)),
            ]
            if self.closing_date:
                triples.append((salary_uri, NS.gr.validThrough, rdflib.Literal(self.closing_date, datatype=NS.xsd.dateTime)))
        elif self.salary:
            triples += [
                (uri, NS.vacancy.salary, salary_uri),
                (salary_uri, NS.rdf.type, NS.gr.UnitPriceSpecification),
                (salary_uri, NS.rdfs.label, rdflib.Literal(self.salary))]
            if self.closing_date:
                triples.append((salary_uri, NS.gr.validThrough, rdflib.Literal(self.closing_date, datatype=NS.xsd.dateTime)))

        return triples

    @property
    def phone_uri(self):
        phone = self.contact_phone
        if phone.startswith('0'):
            phone = '+44' + phone[1:]
        phone = ''.join(d for d in phone if d.isdigit() or d == '+')
        if phone:
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

    class Meta:
        verbose_name_plural = 'vacancies'

class Document(DirtyFieldsMixin, models.Model):
    vacancy = models.ForeignKey(Vacancy)
    url = models.URLField()
    title = models.CharField(max_length=256)
    local_url = models.URLField()
    mimetype = models.CharField(max_length=64, blank=True)
    text = models.TextField()

    def __unicode__(self):
        return u'{0}: {1}'.format(self.vacancy.vacancy_id, self.title)