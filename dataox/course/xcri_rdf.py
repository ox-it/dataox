from __future__ import absolute_import

from humfrey.utils.namespaces import NS
import rdflib

from lxml import builder
from xcri_rdf import XCRICAPSerializer as BaseXCRICAPSerializer, _find_first, serialize_etree

ELIGIBILITY = rdflib.Namespace("http://purl.ox.ac.uk/oxcap/ns/eligibility-")
eligibility_mapping = {ELIGIBILITY.public: 'PU',
                       ELIGIBILITY.members: 'OX',
                       ELIGIBILITY.staff: 'ST'}

VISIBILITY = rdflib.Namespace("http://purl.ox.ac.uk/oxcap/ns/visibility-")
visibility_mapping = {VISIBILITY.public: 'PB',
                      VISIBILITY.restricted: 'RS',
                      VISIBILITY.private: 'PR'}

STATUS = rdflib.Namespace("http://purl.ox.ac.uk/oxcap/ns/status-")
status_mapping = {STATUS.active: 'AC',
                  STATUS.discontinued: 'DC',
                  STATUS.cancelled: 'CN'}

class XCRICAPSerializer(BaseXCRICAPSerializer):
    # Remove xcr:regulations, so we can deal with it as a special case.
    common_descriptive_elements = [(predicate, element)
                                   for (predicate, element)
                                   in BaseXCRICAPSerializer.common_descriptive_elements
                                   if predicate != NS.xcri.regulations]

    xmlns = BaseXCRICAPSerializer.xmlns.copy()
    xmlns.update({'oxcap': 'http://purl.ox.ac.uk/oxcap/ns/'})

    def serialize_common_descriptive_elements(self, xg, entity):
        yield super(XCRICAPSerializer, self).serialize_common_descriptive_elements(xg, entity)

        # We add an attribute based on oxcap:eligibility
        regulations = self.graph.value(entity, NS.xcri.regulations)
        if regulations:
            eligibility = self.graph.value(entity, NS.oxcap.eligibility)
            if eligibility in eligibility_mapping:
                attrib = {'oxcap:eligibility': eligibility_mapping[eligibility]}
            else:
                attrib = {}
            self.descriptive_text_element(xg, 'xcri:regulations', regulations, attrib)

    def course_element(self, xg, course):
        attrib = self.get_visibility_attrib(course)
        attrib.update(self.get_status_attrib(course))
        xg.startElement('xcri:course', attrib)
        yield self.course_content(xg, course)
        xg.endElement('xcri:course')

    def presentation_element(self, xg, presentation):
        attrib = self.get_visibility_attrib(presentation)
        attrib.update(self.get_status_attrib(presentation))
        xg.startElement('xcri:presentation', attrib)
        yield self.presentation_content(xg, presentation)
        xg.endElement('xcri:presentation')

    def presentation_content(self, xg, presentation):
        yield super(XCRICAPSerializer, self).presentation_content(xg, presentation)
        self.serialize_memberApplyTo(xg, presentation)
        self.serialize_bookingEndpoint(xg, presentation)
        self.serialize_missing_applicationProcedure(xg, presentation)
        for session in self.graph.objects(presentation, NS.oxcap.consistsOf):
            yield self.session_element(xg, session)

    def session_element(self, xg, session):
        xg.startElement('oxcap:session', {})
        yield self.session_content(xg, session)
        xg.endElement('oxcap:session')

    def session_content(self, xg, session):
        self.serialize_common_descriptive_elements(xg, session)
        self.serialize_date(xg, session, NS.mlo.start, 'mlo:start')
        self.serialize_date(xg, session, NS.xcri.end, 'xcri:end')

    def get_visibility_attrib(self, entity):
        visibility = self.graph.value(entity, NS.oxcap.visibility)
        if visibility in visibility_mapping:
            return {'oxcap:visibility': visibility_mapping[visibility]}
        else:
            return {}

    def get_status_attrib(self, entity):
        status = self.graph.value(entity, NS.oxcap.status)
        if status in status_mapping:
            return {'oxcap:status': status_mapping[status]}
        else:
            return {}

    def serialize_missing_applicationProcedure(self, xg, presentation):
        if self.graph.value(presentation, NS.xcri.applicationProcedure):
            return
        applyTo = self.graph.value(presentation, NS.xcri.applyTo)
        memberApplyTo = self.graph.value(presentation, NS.oxcap.memberApplyTo)
        if not applyTo and not memberApplyTo:
            return
        if memberApplyTo == applyTo:
            memberApplyTo = None
        E = builder.ElementMaker(namespace=self.xmlns['html'])
        nodes = []
        if memberApplyTo:
            nodes.extend([u"Members of the University of Oxford should apply via ",
                      E.a(unicode(memberApplyTo), href=unicode(memberApplyTo))])
        if memberApplyTo and applyTo:
            nodes.extend([u", and members of the public should apply via ",
                      E.a(unicode(applyTo), href=unicode(applyTo))])
        elif applyTo:
            nodes.extend([u"Apply via ",
                      E.a(unicode(applyTo), href=unicode(applyTo))])
        nodes.append(u'.')
        div = E.div(E.p(*nodes))
        xg.startElement('xcri:applicationProcedure', {})
        serialize_etree(div, xg, previous_nsmap=self.xmlns)
        xg.endElement('xcri:applicationProcedure')


    serialize_memberApplyTo = _find_first('oxcap:memberApplyTo', (NS.oxcap.memberApplyTo,))
    serialize_bookingEndpoint = _find_first('oxcap:bookingEndpoint', (NS.oxcap.bookingEndpoint,))
