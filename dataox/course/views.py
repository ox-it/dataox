from django.http import HttpResponse, Http404
from django_conneg.decorators import renderer
from django_conneg.views import HTMLView, ContentNegotiatedView

from humfrey.elasticsearch import views as elasticsearch_views
from humfrey.linkeddata.views import MappingView
from humfrey.sparql import views as sparql_views
from humfrey.results.views.standard import RDFView
from humfrey.utils.namespaces import NS

import rdflib

import xcri_rdf

class SearchView(elasticsearch_views.SearchView):
    index_name = 'search/courses'

    facets = {'subject': {'terms': {'field': 'subject.uri',
                                        'size': 20}},
              'offeredBy': {'terms': {'field': 'offeredBy.uri',
                                      'size': 20}}}

class CatalogListView(sparql_views.CannedQueryView, HTMLView, RDFView, MappingView):
    template_name = 'course/catalog_list'

    query = """
        DESCRIBE ?catalog ?publisher WHERE {
          ?catalog a xcri:catalog ;
            dcterms:publisher ?publisher .
        }"""

    def get_subjects(self, request, graph, renderers):
        return sorted(map(self.resource, graph.subjects(NS.rdf.type, NS.xcri.catalog)), key=lambda x:x.label)

    def get_additional_context(self, request, renderers):
        return {'renderers': [{'format': r.format,
                               'name': r.name,
                               'mimetypes': r.mimetypes} for r in renderers]}
     

class CatalogDetailView(sparql_views.CannedQueryView, RDFView, ContentNegotiatedView):
    query = """
        CONSTRUCT {
          %(uri)s a xcri:catalog ;
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
          %(uri)s a xcri:catalog ;
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
        DESCRIBE %(uri)s ?course ?presentation ?organisation ?date ?venue ?courseTerm WHERE {
          %(uri)s a xcri:catalog .
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

    def get_query(self, request):
        return self.query % {'uri': rdflib.URIRef(request.GET['uri']).n3()}

    @renderer(format='xcricap', mimetypes=('application/xcri-cap+xml',), name="XCRI-CAP 1.2")
    def render_xcricap(self, request, context, template_name):
        serializer = xcri_rdf.XCRICAPSerializer(context['graph'])
        return HttpResponse(serializer.generator(), mimetype='application/xcri-cap+xml')

class CatalogView(ContentNegotiatedView):
    catalog_detail_view = staticmethod(CatalogDetailView.as_view())
    catalog_list_view = staticmethod(CatalogListView.as_view())

    def get(self, request):
        if 'uri' in request.GET:
            return self.catalog_detail_view(request)
        else:
            return self.catalog_list_view(request, self.catalog_detail_view._renderers)
