# -*- coding: utf-8 -*-

import cgi
import datetime
import email
import urllib
import urlparse
import locale
import logging
import mimetypes
import os
import re
import shutil
import tempfile
import time
import urllib2

import dateutil.parser
import html2text
from lxml import etree
import pytz
import rdflib

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.db import models
from humfrey.elasticsearch.query import ElasticSearchEndpoint
from humfrey.utils.namespaces import NS

from .converters import converters

logger = logging.getLogger(__name__)
email_re = re.compile(r'(?P<localpart>[a-zA-Z\d\-._]+)@(?P<host>[a-zA-Z\d\-.]+)')

category_choices = (
    ('academic', 'Academic'),
    ('support-technical', 'Support and Technical'),
    ('professional-management', 'Professional and Management'),
    ('research', 'Research'),
    ('temporary-staffing-service', 'Temporary Staffing Service'),
)

feed_names = set(['naturejobs', 'jobs-ac-uk', 'all'])
feed_uri_prefix = rdflib.URIRef('https://data.ox.ac.uk/id/vacancy-feed/')

def _parse_http_date(ts):
    return pytz.utc.localize(datetime.datetime(*email.utils.parsedate(ts)[:7]))

class Vacancy(DirtyFieldsMixin, models.Model):
    vacancy_id = models.CharField(max_length=10)
    title = models.CharField(max_length=512)

    location = models.CharField(max_length=1024)
    organizationPart = models.CharField(max_length=256, blank=True)
    formalOrganization = models.CharField(max_length=256, blank=True)
    basedNear = models.CharField(max_length=256, blank=True)
    
    description = models.TextField()
    tags = models.TextField(blank=True)
    category = models.TextField(choices=category_choices, blank=True)
    
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

    def update_location_fields(self, store_slug, department=None):
        # Perform a query against ElasticSearch to find an organization for this location
        search_endpoint = ElasticSearchEndpoint(store_slug, 'organization')
        if department:
            results = search_endpoint.query({'query': {'term': {'finance': department}}})
            try:
                department = results['hits']['hits'][0]['_source']['uri']
            except (IndexError, KeyError):
                logger.error("Couldn't find department for code %s", department)
                department = None
        if department:
            query = {'query': {'bool': {'must': {'term': {'ancestorOrganization.uri': department}},
                                        'should': {'query_string': {'query': self.location.replace('-', ' ')}}}},
                     'filter': {'term': {'graph.uri': 'https://data.ox.ac.uk/graph/oxpoints/data'}}}
        else:
            query = {'query': {'query_string': {'query': self.location.replace('-', ' ')}},
                     'filter': {'term': {'graph.uri': 'https://data.ox.ac.uk/graph/oxpoints/data'}}}

        results = search_endpoint.query(query)
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
        if site_uris:
            query = {'query': {'bool': {'must': {'query_string': {'query': self.location}},
                                        'should': [{'terms': {'uri': site_uris}}]}},
                     'filter': {'term': {'graph.uri': 'https://data.ox.ac.uk/graph/oxpoints/data'}}}
        else:
            query = {'query': {'query_string': {'query': self.location}},
                     'filter': {'term': {'graph.uri': 'https://data.ox.ac.uk/graph/oxpoints/data'}}}
        results = search_endpoint.query(query)
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
                etree.fromstring(self.description)
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

        triples.append((feed_uri_prefix + 'all', NS.skos.member, uri))
        if self.tags:
            tags = set(tag.strip() for tag in self.tags.split(','))
            for tag in tags:
                if tag.lower() in feed_names:
                    triples.append((feed_uri_prefix + tag.lower(), NS.skos.member, uri))
                else:
                    triples.append((uri, NS.dc.subject, rdflib.Literal(tag)))
        if self.category:
            triples.append((uri, NS.dcterms.subject, rdflib.URIRef('https://data.ox.ac.uk/id/vacancy-category/' + self.category)))

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
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.unicode_snob = True
        return h.handle(self.description)

    class Meta:
        verbose_name_plural = 'vacancies'


class Document(DirtyFieldsMixin, models.Model):
    vacancy = models.ForeignKey(Vacancy)
    url = models.URLField(max_length=2048, null=True)
    index = models.IntegerField(null=True)
    title = models.CharField(max_length=256)
    file_path = models.TextField()
    local_url = models.URLField()
    mimetype = models.CharField(max_length=64, blank=True)
    text = models.TextField()

    def __unicode__(self):
        return u'{0}: {1}'.format(self.vacancy.vacancy_id, self.title)

    def ensure_present(self, url):
        if self.file_path:
            return

        file_path_base = os.path.join(settings.SOURCE_DIRECTORY, 'vacancies')
        file_url_base = urlparse.urljoin(settings.SOURCE_URL, 'vacancies/')

        logger.debug("Retrieving vacancy document: %s %d", self.vacancy.vacancy_id, self.index)

        response = urllib2.urlopen(url)

        self.mimetype, _ = cgi.parse_header(response.headers.get('Content-Type') or '')

        try:
            content_disposition = response.headers['Content-Disposition']
            if not content_disposition.startswith('attachment'):
                content_disposition = 'attachment; ' + content_disposition
            target_filename = urllib.quote(cgi.parse_header(content_disposition)[1]['filename'], '')
        except KeyError:
            target_filename = '{0}{1}'.format(self.id, mimetypes.guess_extension(self.mimetype) or '.obj')
        else:
            if self.mimetype in ('binary/octet-stream', 'application/octet-stream'):
                self.mimetype, _ = mimetypes.guess_type(target_filename)

        self.file_path = os.path.join(file_path_base, self.vacancy.vacancy_id.encode('utf-8'), target_filename)
        self.local_url = '%s%s/%s' % (file_url_base, self.vacancy.vacancy_id, target_filename)

        with tempfile.NamedTemporaryFile(delete=False) as f:
            while True:
                block = response.read(4096)
                if not block:
                    break
                f.write(block)

        try:
            last_modified = _parse_http_date(response.headers['last-modified'])
        except KeyError:
            pass
        else:
            last_modified_ts = time.mktime(last_modified.timetuple())
            os.utime(f.name, (last_modified_ts, last_modified_ts))

        if not os.path.exists(os.path.dirname(self.file_path)):
            os.makedirs(os.path.dirname(self.file_path))
        os.chmod(f.name, 0644) # octal, remember
        shutil.move(f.name, self.file_path)

        try:
            converter = converters[self.mimetype]()
        except KeyError:
            logger.warning("Unsupported mimetype for conversion '%s' for file %s",
                           self.mimetype, self.local_url)
            self.text = ''
        else:
            try:
                text = converter.convert_to_text(self.file_path, self.mimetype)
                logger.debug("Converted")
            except Exception:
                logger.exception("Failed to convert %r (%r) to text using %s",
                                 self.local_url, self.mimetype, converter.__class__.__name__)
                self.text = ''
            else:
                text = re.sub(ur'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff]', '', text)
                self.text = text

    def delete(self):
        if self.file_path:
            try:
                os.unlink(self.file_path)
            except IOError:
                logger.exception("Couldn't remove document")
        super(Document, self).delete()
