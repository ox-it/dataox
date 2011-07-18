from __future__ import division

from django.http import Http404, HttpResponse
from django.conf import settings

import rdflib, hashlib, os, urllib
from PIL import Image

from humfrey.desc.views import EndpointView, RDFView, SRXView
from humfrey.utils.namespaces import NS
from humfrey.utils.resource import Resource, expand
from humfrey.utils.views import BaseView
from humfrey.utils.cache import cached_view

class DatasetView(EndpointView, RDFView):
    _QUERY = """
        DESCRIBE ?dataset ?license WHERE {
            ?dataset a void:Dataset ;
                     dcterms:license ?license
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
     'description': 'A re-imagining of <a href="http://www.ox.ac.uk/visitors_f'
       + 'riends/maps_and_directions/science_area.html">the official science a'
       + 'rea map</a> using OpenStreetMap and OxPoints data.'},
)

class ExploreView(BaseView):
    def initial_context(self, request):
        return {
            'examples': EXAMPLES,
        }

    @cached_view
    def handle_GET(self, request, context):
        return self.render(request, context, 'explore')


class ExampleResourceView(EndpointView, SRXView):
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

class ExampleQueryView(EndpointView, SRXView):
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

class HelpView(BaseView):
    @cached_view
    def handle_GET(self, request, context):
        return self.render(request, context, 'help')

class ContactView(BaseView):
    @cached_view
    def handle_GET(self, request, context):
        return self.render(request, context, 'contact')

class ForbiddenView(BaseView):
    @cached_view
    def handle_GET(self, request, context):
        context['status_code'] = 403
        return self.render(request, context, 'forbidden')

class ResizedImageView(EndpointView):
    _image_types = set(map(expand, settings.IMAGE_TYPES))
    
    def initial_context(self, request):
        try:
            url = rdflib.URIRef(request.GET['url'])
            width = int(request.GET['width'])
            types = self.endpoint.query("SELECT ?t WHERE { %s a ?t }" % url.n3())
            if not set(t.t.uri for t in types) & self._image_types:
            	raise TypeError
        except Exception:
            raise Http404
        if width not in (200,):
            raise Http404
            
        filename = hashlib.sha1('%d:%s' % (width, url)).hexdigest()
        filename = [filename[:2], filename[2:4], filename[4:6], filename[6:]]
        filename = os.path.abspath(os.path.join(settings.RESIZED_IMAGE_CACHE_DIR, *filename))

        if not os.path.exists(os.path.dirname(filename)):
        	os.makedirs(os.path.dirname(filename))
        
        if not os.path.exists(filename):
            open(filename, 'w').close()
            temporary_filename, _ = urllib.urlretrieve(url)
            try:
                im = Image.open(temporary_filename)
                size = im.size
                ratio = size[1] / size[0]

                if width >= size[0]:
                    resized = im
                else:
                    resized = im.resize((width, int(round(width*ratio))), Image.ANTIALIAS)
                resized.save(filename, format='jpeg')
            except Exception, e:
                os.unlink(filename)
                raise
            finally:
                os.unlink(temporary_filename)

        return {
            'filename': filename,
            'url': url,
	        'width': width,
	    }
    
    def handle_GET(self, request, context):
        filename = context.pop('filename')
        if settings.DEBUG:
            return HttpResponse(open(filename), mimetype='image/jpeg')
        else:
            response = HttpResponse('', mimetype='image/jpeg')
            response['X-SendFile'] = filename
            return response

        
