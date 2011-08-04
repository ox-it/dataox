from __future__ import division


from humfrey.linkeddata.views import RDFView, ResultSetView
from humfrey.utils.namespaces import NS
from humfrey.utils.resource import Resource
from humfrey.utils.views import BaseView
from humfrey.utils.cache import cached_view

class DatasetView(RDFView):
    _QUERY = """
        DESCRIBE ?dataset ?license ?publisher WHERE {
            ?dataset a void:Dataset ;
                     dcterms:license ?license ;
                     dcterms:publisher ?publisher .
        }"""
        
    def initial_context(self, request):
        graph = self.endpoint.query(self._QUERY)
        datasets = graph.subjects(NS['rdf'].type, NS['void'].Dataset)
        datasets = [Resource(uri, graph, self.endpoint) for uri in datasets]
        datasets.sort(key=lambda ds:unicode(ds.label))
        return {
            'graph': graph,
            'datasets': datasets,
        }
    
    @cached_view
    def handle_GET(self, request, context):
        return self.render(request, context, 'datasets')

EXAMPLES = (
    {'slug': 'science-area',
     'name': 'Science Area Map',
     'description': 'A re-imagining of <a href="http://www.ox.ac.uk/visitors_f'
       + 'riends/maps_and_directions/science_area.html">the official science a'
       + 'rea map</a> using OpenStreetMap and OxPoints data.'},
    {'slug': 'openmeters',
     'name': 'OpenMeters',
     'description': 'Graphical representations of the University of Oxford's electricity usage.'},
    {'slug': 'vacancy-treemap',
     'name': 'Vacancy Treemap',
     'description': 'The distribution of job vacancies across the University.'},
)

class ExploreView(BaseView):
    def initial_context(self, request):
        return {
            'examples': EXAMPLES,
        }

    @cached_view
    def handle_GET(self, request, context):
        return self.render(request, context, 'explore')


class ExampleResourceView(ResultSetView):
    _QUERY = """
        SELECT ?resource ?dataset WHERE {
            ?dataset void:exampleResource ?resource .
        } ORDER BY ?dataset ?resource"""

    def initial_context(self, request):
        return {
            'results': self.endpoint.query(self._QUERY),
        }

    @cached_view
    def handle_GET(self, request, context):
        return self.render(request, context, 'explore-resource')

class ExampleQueryView(ResultSetView):
    _QUERY = """
        SELECT ?dataset ?value ?label ?comment WHERE {
            ?dataset oo:exampleQuery [
                rdf:value ?value ;
                rdfs:label ?label ;
                rdfs:comment ?comment ]
        }"""
    def initial_context(self, request):
        return {
            'results': self.endpoint.query(self._QUERY),
        }
    @cached_view
    def handle_GET(self, request, context):
        return self.render(request, context, 'explore-query') 

class ExampleDetailView(BaseView):
    @cached_view
    def handle_GET(self, request, context, slug):
        return self.render(request, context, 'examples/%s' % slug)

class ForbiddenView(BaseView):
    @cached_view
    def handle_GET(self, request, context):
        context['status_code'] = 403
        return self.render(request, context, 'forbidden')

        
