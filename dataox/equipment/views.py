import httplib
import urllib2
try:
    import json
except ImportError:
    import simplejson

from django_conneg.views import HTMLView, JSONPView
from django.conf import settings
from django.http import Http404
import rdflib

from humfrey.desc import views as desc_views
from humfrey.elasticsearch import views as elasticsearch_views
from humfrey.linkeddata.views import MappingView
from humfrey.results.views.standard import RDFView
from humfrey.sparql.views import StoreView, CannedQueryView
from humfrey.utils.namespaces import NS
from humfrey.utils.resource import BaseResource

class EquipmentView(object):
    """
    Mixin to choose between public and internal indexes.
    """

    @property
    def store_name(self):
        if self.request.user.groups.filter(name='member').count():
            return 'equipment'
        else:
            return 'public'

    @property
    def index_name(self):
        return '{0}/equipment'.format(self.store_name)

class DescView(EquipmentView, desc_views.DescView):
    pass

class DocView(EquipmentView, desc_views.DocView):
    template_name = 'equipment/view'

class SearchView(EquipmentView, elasticsearch_views.SearchView):
    facets = {'department': {'terms': {'field': 'equipmentOf.uri',
                                        'size': 20}},
              'basedNear': {'terms': {'field': 'basedNear.uri',
                                      'size': 20}},
              'institution': {'terms': {'field': 'formalOrganisation.uri',
                                        'size': 20}},
              'oxford': {'terms': {'field': 'oxfordUniversityEquipment'}},
              'category': {'terms': {'field': 'category.uri'}},
              'subcategory': {'terms': {'field': 'subcategory.uri'}}}
    
    template_name = 'equipment/search'

#class ItemView(EquipmentView, HTMLView, JSONPView):
#    def get(self, request, id):
#        try:
#            url = ('http://%(host)s:%(port)s/%s/' % (settings.ELASTICSEARCH_SERVER, self.index_name)) + id
#            item = elasticsearch_views.SearchView.Deunderscorer(json.load(urllib2.urlopen(url)))
#        except urllib2.HTTPError, e:
#            if e.code == httplib.NOT_FOUND:
#                raise Http404
#            raise
#        
#        more_like_this_url = url + '/_mlt?min_doc_freq=1'
#        
#        context = {'item': item,
#                   'more_like_this': elasticsearch_views.SearchView.Deunderscorer(json.load(urllib2.urlopen(more_like_this_url)))}
#        
#        return self.render(request, context, 'equipment/item')

class BrowseView(EquipmentView, HTMLView, RDFView, CannedQueryView, MappingView):
    concept_scheme = rdflib.URIRef('http://data.ox.ac.uk/id/equipment-category')
    datatype = rdflib.URIRef('http://data.ox.ac.uk/id/notation/equipment-category')

    template_name = 'equipment/browse'

    @property
    def notation(self):
        if self.kwargs.get('notation'):
            return rdflib.Literal(self.kwargs['notation'], datatype=self.datatype)

    def get_query(self, request, notation):
        if self.notation:
            return """
                DESCRIBE ?concept ?narrower ?equipment WHERE {{
                  ?concept skos:notation {} .
                  OPTIONAL {{ ?equipment dcterms:subject ?concept }} .
                  OPTIONAL {{ ?concept skos:narrower ?narrower }}
                }}""".format(self.notation.n3())
        else:
            return """
                CONSTRUCT {{
                 {concept_scheme} a skos:ConceptScheme ;
                    skos:prefLabel ?conceptSchemeLabel ;
                    skos:hasTopConcept ?concept .
                  ?concept a skos:Concept ;
                    skos:prefLabel ?conceptLabel ;
                    skos:notation ?conceptNotation ;
                    
                }} WHERE {{
                  {concept_scheme} a skos:ConceptScheme ;
                    skos:prefLabel ?conceptSchemeLabel .
                  {{
                    SELECT ?concept ?conceptLabel ?conceptNotation (COUNT(?equipment) as ?equipmentCount) WHERE {{
                      {concept_scheme} skos:hasTopConcept ?concept .
                      ?concept a skos:Concept ;
                        skos:prefLabel ?conceptLabel ;
                        skos:notation ?conceptNotation ;
                        skos:narrower*/^dcterms:subject ?equipment .
                    }} GROUP BY ?concept ?conceptLabel ?conceptNotation 
                  }}
                    
                }}""".format(concept_scheme=self.concept_scheme.n3())

    def finalize_context(self, request, context, notation):
        graph = context['graph']
        context['equipment'] = map(self.resource, graph.subjects(NS.rdf.type, NS.oo.Equipment))
        context['equipment'].sort(key=lambda s:s.label)
        if self.notation:
            concept = graph.value(None, NS.skos.notation, self.notation)
            context['concept'] = self.resource(concept)
            context['concepts'] = map(self.resource, graph.objects(concept, NS.skos.narrower))
        else:
            context['concepts'] = map(self.resource, graph.objects(self.concept_scheme, NS.skos.hasTopConcept))
        context['concepts'].sort(key=lambda s:s.label)
        print context
        return context
