# -*- coding: utf-8 -*-

import locale

from lxml import etree
import rdflib

from django.conf import settings
from django.db import models
from humfrey.utils.namespaces import NS

class Vacancy(models.Model):
    vacancy_id = models.CharField(max_length=10)
    title = models.CharField(max_length=512)

    location = models.CharField(max_length=1024)
    organizationalPart = models.CharField(max_length=256, blank=True)
    formalOrganization = models.CharField(max_length=256, blank=True)
    
    description = models.TextField()
    
    salary = models.CharField(max_length=128, blank=True)
    salary_grade = models.CharField(max_length=32, blank=True)
    salary_lower = models.PositiveIntegerField(null=True, blank=True)
    salary_upper = models.PositiveIntegerField(null=True, blank=True)
    salary_discretionary = models.PositiveIntegerField(null=True, blank=True)

    contact_name = models.CharField(max_length=128, blank=True)
    contact_email = models.CharField(max_length=128, blank=True)
    contact_phone = models.CharField(max_length=128, blank=True)
    
    url = models.URLField(max_length=2048, blank=True)
    apply_url = models.URLField(max_length=2048, blank=True)

    opening_date = models.DateTimeField()
    closing_date = models.DateTimeField()
    
    internal = models.BooleanField()
    
    def __unicode__(self):
        return u'{0}: {1}'.format(self.vacancy_id, self.title)

    def triples(self, base_uri):
        uri = rdflib.URIRef(base_uri + self.vacancy_id)
        contact_uri = rdflib.URIRef(uri + '/contact')
        salary_uri = rdflib.URIRef(uri + '/salary')

        triples = [
            (uri, NS.rdf.type, NS.vacancy.Vacancy),
            (uri, NS.foaf.homepage, rdflib.URIRef(self.url)),
            (uri, NS.oo.contact, contact_uri),
            (uri, NS.vacancy.applicationOpeningDate, rdflib.Literal(self.opening_date)),
            (uri, NS.vacancy.applicationClosingDate, rdflib.Literal(self.closing_date)),
            (uri, NS.vacancy.internalApplicationsOnly, rdflib.Literal(self.internal)),
            (uri, NS.rdfs.label, rdflib.Literal(self.title)),
        ]

        if self.contact_name or self.contact_email or self.contact_phone:
            triples += [(uri, NS.oo.contact, contact_uri),
                        (contact_uri, NS.rdf.type, NS.foaf.Agent)]
        if self.contact_name:
            triples.append((contact_uri, NS.foaf.name, rdflib.Literal(self.contact_name)))
        if self.contact_email:
            triples.append((contact_uri, NS.v.email, rdflib.URIRef(self.contact_email)))
        if self.contact_phone:
            phone_uri = self.phone_uri
            triples += [(contact_uri, NS.v.tel, phone_uri),
                        (phone_uri, NS.rdf.type, NS.v.Voice),
                        (phone_uri, NS.rdf.value, rdflib.Literal(self.contact_phone))]

        if self.description:
            triples += [
                (uri, NS.rdfs.comment, rdflib.Literal(self.description, datatype=NS.xtypes['Fragment-XHTML'])),
                (uri, NS.rdfs.comment, rdflib.Literal(self.plain_description)),
            ]
        for formalOrganization in self.formalOrganization.split():
            triples.append((uri, NS.oo.formalOrganization, rdflib.URIRef(formalOrganization)))
        for organizationalPart in self.organizationalPart.split():
            triples.append((uri, NS.oo.organizationalPart, rdflib.URIRef(organizationalPart)))

        for document in self.document_set.all():
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

            triples += [
                (uri, NS.vacancy.salary, salary_uri),
                (salary_uri, NS.rdf.type, NS.gr.UnitPriceSpecification),
                (salary_uri, NS.rdfs.label, rdflib.Literal(label)),
                (salary_uri, NS.gr.validThrough, rdflib.Literal(self.closing_date)),
                (salary_uri, NS.gr.hasCurrency, rdflib.Literal('GBP')),
            ]
        elif self.salary:
            triples += [
                (uri, NS.vacancy.salary, salary_uri),
                (salary_uri, NS.rdf.type, NS.gr.UnitPriceSpecification),
                (salary_uri, NS.rdfs.label, rdflib.Literal(self.salary)),
                (salary_uri, NS.gr.validThrough, rdflib.Literal(self.closing_date))]

        return triples

    @property
    def phone_uri(self):
        phone = self.contact_phone
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


class Document(models.Model):
    vacancy = models.ForeignKey(Vacancy)
    url = models.URLField()
    title = models.CharField(max_length=256)
    local_url = models.URLField()
    mimetype = models.CharField(max_length=64, blank=True)
    text = models.TextField()

    def __unicode__(self):
        return u'{0}: {1}'.format(self.vacancy.vacancy_id, self.title)
