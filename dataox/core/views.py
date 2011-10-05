from __future__ import division

from django_conneg.views import HTMLView

from humfrey.utils.views import CachedView, RedisView
from humfrey.browse import views as browse_views
from humfrey.results.views.standard import RDFView, ResultSetView
from humfrey.utils.namespaces import NS
from humfrey.utils.resource import Resource

class DatasetView(RDFView, HTMLView, CachedView):
    _QUERY = """
        DESCRIBE ?dataset ?license ?publisher WHERE {
            ?dataset a void:Dataset ;
                     dcterms:license ?license ;
                     dcterms:publisher ?publisher .
        }"""

    def get(self, request):
        graph = self.endpoint.query(self._QUERY)
        datasets = graph.subjects(NS['rdf'].type, NS['void'].Dataset)
        datasets = [Resource(uri, graph, self.endpoint) for uri in datasets]
        datasets.sort(key=lambda ds:unicode(ds.label))

        context = {
            'graph': graph,
            'datasets': datasets,
        }

        return self.render(request, context, 'datasets')

EXAMPLES = (
    {'slug': 'science-area',
     'name': 'Science Area Map',
     'description': 'A re-imagining of <a href="http://www.ox.ac.uk/visitors_f'
       + 'riends/maps_and_directions/science_area.html">the official science a'
       + 'rea map</a> using OpenStreetMap and OxPoints data.'},
    {'slug': 'openmeters',
     'name': 'OpenMeters',
     'description': "Graphical representations of the University of Oxford's electricity usage."},
    {'slug': 'vacancy-treemap',
     'name': 'Vacancy Treemap',
     'description': 'The distribution of job vacancies across the University.'},
	{'slug': 'unicard-explorer',
     'name': 'University Card Explorer',
     'description': 'A tool for exploring statistics about the Oxford\'s bod (university) cards.'},
    {'slug': 'feed-creator',
     'name': 'Feed Creator',
     'description': 'Create your own feed (eg RSS, Atom) of data in data.ox!'},
)

class ExploreView(HTMLView, CachedView, RedisView):
    def get(self, request):
        context = {
            'examples': EXAMPLES,
            'lists': self.unpack(self.get_redis_client().get(browse_views.IndexView.LIST_META)),
        }
        return self.render(request, context, 'explore')

class ExampleResourceView(ResultSetView, HTMLView, CachedView):
    _QUERY = """
        CONSTRUCT {
            ?dataset a void:Dataset ;
              rdfs:label ?datasetLabel ;
              void:exampleResource ?resource .
            ?resource ?p ?resourceLabel .
        } WHERE {
            ?dataset a void:Dataset ;
              rdfs:label ?datasetLabel ;
              void:exampleResource ?resource .
            ?resource ?p ?resourceLabel .
            FILTER (?p in (rdfs:label, dc:title, dcterms:title, foaf:name)) .
        }"""

    def get(self, request):
        graph = self.endpoint.query(self._QUERY)
        context = {
            'graph': graph,
            'subjects': [Resource(uri, graph, self.endpoint) for uri in graph.subjects(NS.rdf.type, NS.void.Dataset)],
        }

        return self.render(request, context, 'explore-resource')

class ExampleQueryView(ResultSetView, HTMLView, CachedView):
    _QUERY = """
        SELECT ?dataset ?datasetLabel ?value ?label ?comment WHERE {
            ?dataset a void:Dataset ;
              rdfs:label ?datasetLabel ;
              oo:exampleQuery [
                rdf:value ?value ;
                rdfs:label ?label ;
                rdfs:comment ?comment ]
        }"""

    def get(self, request):
        context = {
            'results': self.endpoint.query(self._QUERY),
        }

        return self.render(request, context, 'explore-query') 

class ExampleDetailView(HTMLView, CachedView):
    def get(self, request, slug):
        return self.render(request, {}, 'examples/%s' % slug)

class ForbiddenView(HTMLView, CachedView):
    def get(self, request):
        context = {
            'status_code': 403,
        }
        return self.render(request, context, 'forbidden')
