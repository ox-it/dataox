from __future__ import division

from django_conneg.views import HTMLView

from humfrey.utils.views import CachedView
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
	{'slug': 'bodcardbrowser',
     'name': 'University Card Statistics Explorer',
     'description': 'A tool for exploring monthly statistics about the Oxford\'s University (Bod) Cards.'},
)

class ExploreView(HTMLView, CachedView):
    def get(self, request):
        context = {
            'examples': EXAMPLES,
        }
        return self.render(request, context, 'explore')

class ExampleResourceView(ResultSetView, HTMLView, CachedView):
    _QUERY = """
        SELECT ?resource ?dataset WHERE {
            ?dataset void:exampleResource ?resource .
        } ORDER BY ?dataset ?resource"""

    def get(self, request):
        context = {
            'results': self.endpoint.query(self._QUERY),
        }

        return self.render(request, context, 'explore-resource')

class ExampleQueryView(ResultSetView, HTMLView, CachedView):
    _QUERY = """
        SELECT ?dataset ?value ?label ?comment WHERE {
            ?dataset oo:exampleQuery [
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
