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

class XCRICAPSerializer(BaseXCRICAPSerializer):
    # Remove xcr:regulations, so we can deal with it as a special case.
    common_descriptive_elements = [(predicate, element)
                                   for (predicate, element)
                                   in BaseXCRICAPSerializer.common_descriptive_elements
                                   if predicate != NS.xcri.regulations]

    def serialize_common_descriptive_elements(self, xg, entity):
        super(XCRICAPSerializer, self).serialize_common_descriptive_elements(xg, entity)

        # We add an attribute based on oxcap:eligibility
        regulations = self.graph.value(entity, NS.xcri.regulations)
        if regulations:
            eligibility = self.graph.value(entity, NS.oxcap.eligibility)
            if eligibility in eligibility_mapping:
                attrib = {'oxcap:eligibility': eligibility_mapping[eligibility]}
            else:
                attrib = None
            self.descriptive_text_element(xg, 'xcri:eligibility', regulations, attrib)

    def course_element(self, xg, course):
        xg.startElement('xcri:course', self.get_visibility_attrib(course))
        yield self.course_content(xg, course)
        xg.endElement('xcri:course')

    def presentation_element(self, xg, presentation):
        xg.startElement('xcri:presentation', self.get_visibility_attrib(presentation))
        yield self.course_content(xg, presentation)
        xg.endElement('xcri:presentation')

    def presentation_content(self, xg, presentation):
        super(XCRICAPSerializer, self).presentation_content(xg, presentation)
        self.serialize_memberApplyTo(xg, presentation)

    def get_visibility_attrib(self, entity):
        visibility = self.graph.value(entity, NS.oxcap.visibility)
        if visibility in visibility_mapping:
            return {'oxcap:visibility': visibility_mapping[visibility]}
        else:
            return {}

    serialize_memberApplyTo = _find_first('oxcap:applyTo', (NS.oxcap.memberApplyTo,))