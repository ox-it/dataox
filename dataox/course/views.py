from django.http import HttpResponse
from django_conneg.decorators import renderer
from django_conneg.views import HTMLView

from humfrey.elasticsearch import views as elasticsearch_views
from humfrey.misc import views as misc_views
from humfrey.results.views.standard import RDFView

import xcri_rdf

class SearchView(elasticsearch_views.SearchView):
    index_name = 'search/courses'

    facets = {'subject': {'terms': {'field': 'subject.uri',
                                        'size': 20}},
              'offeredBy': {'terms': {'field': 'offeredBy.uri',
                                      'size': 20}}}

class FeedView(misc_views.CannedQueryView, HTMLView, RDFView):
    query = """
        CONSTRUCT {
          ?catalog a xcri:catalog ;
            dcterms:description ?catalogDescription ;
            dcterms:publisher ?provider ;
            skos:member ?course .

          ?provider a ?providerType ;
            rdfs:label ?providerTitle .

          ?course rdf:type ?courseType ;
            rdfs:label ?courseTitle ;
            dcterms:description ?courseDescription ;
            dcterms:subject ?subject ;
            mlo:specifies ?presentation .

          ?presentation rdf:type ?presentationType ;
            xcri:attendanceMode ?attendanceMode ;
            xcri:attendancePattern ?attendancePattern ;
            xcri:studyMode ?studyMode .

          ?subject rdfs:label ?subjectLabel ; skos:notation ?subjectNotation .
          ?attendanceMode rdfs:label ?attendanceModeLabel ; skos:notation ?attendanceModeNotation .
          ?attendancePattern rdfs:label ?attendancePatternLabel ; skos:notation ?attendancePatternNotation .
          ?studyMode rdfs:label ?studyModeTitle .
        } WHERE {
          ?catalog a xcri:catalog ;
            skos:member ?course .
          OPTIONAL { ?catalog dcterms:description|dc:description ?catalogDescription } .
          OPTIONAL {
            ?catalog dcterms:publisher ?provider .
            ?provider a ?providerType .
            OPTIONAL { ?provider rdfs:label|skos:prefLabel|dc:title|dcterms:title ?providerTitle } .
          } .
          ?course rdf:type ?courseType ;
            rdfs:label ?courseTitle ;
            mlo:specifies ?presentation .
          OPTIONAL { ?course dcterms:description|dc:description ?courseDescription } .
          OPTIONAL {
            ?course dcterms:subject ?subject .
            OPTIONAL {?subject rdfs:label|skos:prefLabel ?subjectLabel }
          } .
          OPTIONAL {
            ?course mlo:specifies ?presentation . 
            OPTIONAL { ?presentation xcri:attendanceMode ?attendanceMode .
              OPTIONAL { ?attendanceMode skos:prefLabel ?attendanceModeLabel } .
              OPTIONAL { ?attendanceMode skos:notation ?attendanceModeNotation }
            } .
            OPTIONAL { ?presentation xcri:attendancePattern ?attendancePattern .
              OPTIONAL { ?attendancePattern skos:prefLabel ?attendancePatternLabel } .
              OPTIONAL { ?attendancePattern skos:notation ?attendancePatternNotation }
            } .
            OPTIONAL { ?presentation xcri:studyMode ?studyMode .
              OPTIONAL { ?studyMode skos:prefLabel ?studyModeLabel } .
              OPTIONAL { ?studyMode skos:notation ?studyModeNotation }
            }
          }
        }
    """

    query = """
        DESCRIBE ?catalog ?course ?presentation ?organisation ?date ?venue ?courseTerm WHERE {
          ?catalog a xcri:catalog .
          OPTIONAL {
            ?catalog dcterms:publisher ?organisation
          } .
          OPTIONAL {
            ?catalog skos:member ?course .
            OPTIONAL {
              ?course mlo:specifies ?presentation .
              OPTIONAL { ?presentation mlo:start|xcri:end ?date } .
              OPTIONAL { ?presentation xcri:venue ?venue } .
            } .
            OPTIONAL { ?course dcterms:subject|xcri:attendanceMode|xcri:attendancePattern|xcri:stufyMode ?courseTerm } .
          }
        }
    """

    @renderer(format='xcricap', mimetypes=('application/xcri-cap+xml',), name="XCRI-CAP 1.2")
    def render_xcricap(self, request, context, template_name):
        serializer = xcri_rdf.XCRICAPSerializer(context['graph'])
        return HttpResponse(serializer.generator(), mimetype='application/xcri-cap+xml')