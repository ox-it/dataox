from django.http import HttpResponse, Http404
from django_conneg.decorators import renderer
from django_conneg.views import HTMLView, ContentNegotiatedView
from django_hosts import reverse_full

from humfrey.desc import views as desc_views
from humfrey.elasticsearch import views as elasticsearch_views
from humfrey.linkeddata.views import MappingView
from humfrey.sparql import views as sparql_views
from humfrey.sparql.models import Store
from humfrey.results.views.standard import RDFView
from humfrey.utils.namespaces import NS

import rdflib

from .xcri_rdf import XCRICAPSerializer

class CourseView(object):
    """
    Mixin to choose between public and internal indexes.
    """

    @property
    def desc_view(self):
        return reverse_full('data', 'desc')

    @property
    def doc_view(self):
        return reverse_full('data', 'doc-generic')

    @property
    def store_name(self):
        try:
            return self._store_name
        except AttributeError:
            store = Store.objects.get(slug='courses')
            if self.request.user.has_perm('sparql.query_store', store):
                self._store_name = 'courses'
            else:
                self._store_name = 'public'
            return self._store_name

class IdView(CourseView, desc_views.IdView): pass
class DocView(CourseView, desc_views.DocView): pass

class SearchView(CourseView, elasticsearch_views.SearchView):
    default_types = ('course',)

    facets = {'subject': {'terms': {'field': 'subject.uri',
                                        'size': 20}},
              'offeredBy': {'terms': {'field': 'offeredBy.uri',
                                      'size': 20}}}

class CatalogListView(CourseView, sparql_views.CannedQueryView, HTMLView, RDFView, MappingView):
    template_name = 'course/catalog_list'

    @property
    def query(self):
        return """\
CONSTRUCT {{
  {url} foaf:topic ?catalog .
  ?catalog ?catalogPredicate ?catalogObject .
  ?publisher ?publisherPredicate ?publisherObject
}} WHERE {{
  VALUES ?catalogPredicate {{
    rdf:type
    rdfs:label
    rdfs:comment
    dcterms:title
    dcterms:description
    dcterms:publisher
    dcterms:license
    skos:notation
  }}
  VALUES ?publisherPredicate {{
    rdf:type
    rdfs:label
    skos:prefLabel
    skos:notation
  }}
  ?catalog a xcri:catalog ;
    ?catalogPredicate ?catalogObject ;
    dcterms:publisher ?publisher .
  ?publisher ?publisherPredicate ?publisherObject
}}""".format(url=rdflib.URIRef(self.request.build_absolute_uri()).n3())

    def get_additional_context(self, request, renderers):
        return {'feed_renderers': [{'format': r.format,
                                    'name': r.name,
                                    'mimetypes': r.mimetypes} for r in renderers]}

class CatalogDetailView(CourseView, sparql_views.CannedQueryView, RDFView, ContentNegotiatedView):
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
          OPTIONAL { ?catalog dcterms:description|dc:description|rdfs:comment ?catalogDescription } .
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
        DESCRIBE ?catalog ?provider ?course ?presentation ?organisation ?date ?venue ?courseTerm ?cv ?subject ?session ?sessionDate WHERE {
          %(uri)s skos:member* ?catalog . ?catalog a xcri:catalog .
          OPTIONAL {
            ?catalog dcterms:publisher ?organisation
          } .
          OPTIONAL {
            ?catalog skos:member+ ?course .
            ?course a xcri:course .
            OPTIONAL {
              ?course dcterms:subject/skos:related?/(^skos:narrower|skos:broader)* ?subject
            } .
            OPTIONAL {
              ?course mlo:specifies ?presentation .
              OPTIONAL { ?presentation mlo:start|xcri:end|xcri:applyFrom|xcri:applyUntil ?date } .
              OPTIONAL { ?presentation xcri:attendanceMode|xcri:attendancePattern|xcri:studyMode ?cv } .
              OPTIONAL { ?presentation xcri:venue ?venue } .
              OPTIONAL {
                ?presentation oxcap:consistsOf ?session .
                OPTIONAL { ?session mlo:start|xcri:end ?sessionDate }
              }
            } .
            OPTIONAL { ?provider mlo:offers ?course } .
          }
        }
    """

    @property
    def catalog_uri(self):
        try:
            return rdflib.URIRef(self.request.GET['uri'])
        except KeyError:
            raise Http404

    def get_query(self, request):
        return self.query % {'uri': self.catalog_uri.n3()}

    @renderer(format='xcricap', mimetypes=('application/xcri-cap+xml',), name="XCRI-CAP 1.2 (Simple)")
    def render_xcricap(self, request, context, template_name):
        graph = context['graph']()
        self.wrangle_two_three_codes(graph)
        serializer = XCRICAPSerializer(graph, self.catalog_uri)
        return HttpResponse(serializer.generator(), mimetype='application/xcri-cap+xml')

    @renderer(format='xcricap-full', mimetypes=(), name="XCRI-CAP 1.2 (Full)")
    def render_xcricap_full(self, request, context, template_name):
        graph = context['graph']()
        self.wrangle_two_three_codes(graph)
        serializer = XCRICAPSerializer(graph, self.catalog_uri, simple=False)
        return HttpResponse(serializer.generator(), mimetype='application/xcri-cap+xml')

    def wrangle_two_three_codes(self, graph):
        """
        Pretend an OxPoints ID is a two-three code where one doesn't exist

        WebLearn requires every provider to have a two-three or department
        code. This is a manky hack to add a fake two-three code cotaining the
        OxPoints ID where a two-three code doesn't already exist.
        """
        # Find all things with an OxPoints ID...
        for s, o in graph.subject_objects(NS.skos.notation):
            if getattr(o, 'datatype', None) == NS.oxnotation.oxpoints:
                # ... check they don't have a two-three code ...
                if not any(n for n in graph.objects(s, NS.skos.notation)
                             if getattr(n, 'datatype', None) == NS.oxnotation.twoThree):
                    # ... and add a fake two-three code using the OxPoints ID
                    graph.add((s,
                               NS.skos.notation,
                               rdflib.Literal(o, datatype=NS.oxnotation.twoThree)))


class CatalogView(CourseView, ContentNegotiatedView):
    catalog_detail_view = staticmethod(CatalogDetailView.as_view())
    catalog_list_view = staticmethod(CatalogListView.as_view())

    def get(self, request):
        if 'uri' in request.GET:
            return self.catalog_detail_view(request)
        else:
            return self.catalog_list_view(request, self.catalog_detail_view.conneg.renderers)
