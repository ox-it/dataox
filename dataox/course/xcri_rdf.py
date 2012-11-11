from __future__ import absolute_import

from humfrey.utils.namespaces import NS
import rdflib

from xcri_rdf import XCRICAPSerializer as BaseXCRICAPSerializer, _find_first

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
        for session in self.graph.objects(presentation, NS.prog.has_event):
            yield self.session_element(xg, session)

    def session_element(self, xg, session):
        xg.startElement('oxcap:session', {})
        yield self.session_content(xg, session)
        xg.endElement('oxcap:session')

    def session_content(self, xg, session):
        pass

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

    serialize_memberApplyTo = _find_first('oxcap:applyTo', (NS.oxcap.memberApplyTo,))
    serialize_bookingEndpoint = _find_first('oxcap:bookingEndpoint', (NS.oxcap.bookingEndpoint,))
