import functools

from django.conf import settings
from django.http import Http404
from django.template import loader, RequestContext
from django.urls import reverse
from django.core.mail import EmailMessage
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django_conneg.http import HttpResponseSeeOther
from django_conneg.views import HTMLView
import rdflib

from humfrey.desc import views as desc_views
from humfrey.elasticsearch import views as elasticsearch_views
from humfrey.linkeddata.resource import Resource
from humfrey.linkeddata.views import MappingView
from humfrey.results.views.standard import RDFView
from humfrey.sparql.models import Store
from humfrey.sparql.views import CannedQueryView, StoreView
from humfrey.utils.namespaces import NS

from . import forms, resource

class EquipmentView(object):
    """
    Mixin to choose between public and internal indexes.
    """
    
    id_mapping = (('https://data.ox.ac.uk/id/equipment/', 'https://www.research-facilities.ox.ac.uk/view:equipment/', True),
                  ('https://data.ox.ac.uk/id/facility/', 'https://www.research-facilities.ox.ac.uk/view:facility/', True),
                  ('http://id.southampton.ac.uk/', 'https://www.research-facilities.ox.ac.uk/view:soton/', False),
                  ('http://oxpoints.oucs.ox.ac.uk/id/', 'https://www.research-facilities.ox.ac.uk/view:oxpoints/', False))

    resource_registry = resource.resource_registry

    @property
    def desc_url(self):
        return reverse('desc')

    @property
    def doc_url(self):
        return reverse('doc-generic')

    @property
    def store_name(self):
        try:
            return self._store_name
        except AttributeError:
            store = Store.objects.get(slug='equipment')
            if self.request.user.has_perm('sparql.query_store', store):
                self._store_name = 'equipment'
            else:
                self._store_name = 'public'
            return self._store_name

class DescView(EquipmentView, desc_views.DescView):
    pass

class DocView(EquipmentView, desc_views.DocView):
    template_name = 'equipment/view/base'

class ContributeView(HTMLView, MappingView, StoreView):
    recipients_to = [('Research Services', 'research.facilities@admin.ox.ac.uk')]
    recipients_cc = [('Open Data Team', 'opendata-admin@maillist.ox.ac.uk')]

    @method_decorator(login_required(login_url='/shibboleth-login/'))
    def dispatch(self, request):
        return super(ContributeView, self).dispatch(request)

    def common(self, request):
        self.context.update({'form': forms.ContributeForm(request.POST or None)})

    def get(self, request):
        if 'submitted' in request.GET:
            return self.render(request, {}, 'equipment/contribute-submitted')

        self.common(request)
        return self.render(request, self.context, 'equipment/contribute')

    autocompleted_fields = ('category', 'department', 'place')
    def resolve_autocompleted_fields(self, fields, cleaned_data):
        """
        Some of the fields are autocompleted and return URIs; this looks up
        those URIs so we can re-attach labels to them.
        """
        uri = lambda k: rdflib.URIRef(cleaned_data[k])
        query = "DESCRIBE {0}".format(' '.join(uri(k).n3() for k in fields))
        graph = self.endpoint.query(query)
        resource = functools.partial(Resource, graph=graph, endpoint=self.endpoint)
        return dict((k, resource(uri(k))) for k in fields if k in cleaned_data)

    def post(self, request):
        self.common(request)
        if not self.context['form'].is_valid():
            return self.get(request)

        template = loader.get_template("equipment/contribute.eml")
        context = {'data': self.context['form'].cleaned_data}
        context.update(self.resolve_autocompleted_fields(self.autocompleted_fields,
                                                         self.context['form'].cleaned_data))
        body = template.render(RequestContext(request, context))

        message = EmailMessage("New equipment listing",
                               body=body,
                               to=['%s <%s>' % recipient for recipient in self.recipients_to],
                               cc=['%s <%s>' % recipient for recipient in self.recipients_cc],
                               #from_email="{0.first_name} {0.last_name} (via www.research-facilities.ox.ac.uk) <{1}>".format(request.user, settings.SERVER_EMAIL),
                               headers={#'From': "{0.first_name} {0.last_name} (via www.research-facilities.ox.ac.uk) <{1}>".format(request.user, settings.SERVER_EMAIL),
                                        'Sender': settings.SERVER_EMAIL,
                                        'Reply-To': request.user.email})
        message.send(fail_silently=False)
        return HttpResponseSeeOther("?submitted=true")

class SearchView(EquipmentView, elasticsearch_views.SearchView):
    @property
    def aggregations(self):
        aggregations = {
            'institution': {'terms': {'field': 'formalOrganisation.uri', 'size': 100}},
            'basedNear': {'terms': {'field': 'basedNear.uri', 'size': 100}},
            'category': {'terms': {'field': 'category.uri'}},
            'shareability': {'terms': {'field': 'shareability.uri'}},
        }
        if 'filter.formalOrganisation.uri' in self.request.GET:
            aggregations['department'] = {'terms': {'field': 'equipmentOf.uri', 'size': 100}}
        if 'filter.category.uri' in self.request.GET:
            aggregations['subcategory'] = {'terms': {'field': 'subcategory.uri'}}
        return aggregations

        #          'oxford': {'terms': {'field': 'oxfordUniversityEquipment'}},

    template_name = 'equipment/search'
    default_types = ('equipment', 'facility', 'service')

    dependent_parameters = {'filter.category.uri': ('filter.subcategory.uri',),
                            'filter.formalOrganisation.uri': ('filter.equipmentOf.uri',)}

    def finalize_context(self, request, context):
        if not context.get('q'):
            context['form'] = forms.AdvancedSearchForm(request.GET or None,
                                                       search_url=self.search_endpoint.search_url,
                                                       store=self.store)
        return context

class BrowseView(EquipmentView, CannedQueryView, RDFView, HTMLView, MappingView):
    concept_scheme = rdflib.URIRef('https://data.ox.ac.uk/id/equipment-category')
    datatype = rdflib.URIRef('https://data.ox.ac.uk/id/notation/equipment-category')

    template_name = 'equipment/browse'

    @property
    def notation(self):
        if self.kwargs.get('notation'):
            return rdflib.Literal(self.kwargs['notation'], datatype=self.datatype)
    
    def get_query(self, request, notation):
        if self.notation:
            return """
                DESCRIBE ?concept ?narrower ?equipment ?narrowerEquipment ?other ?broader WHERE {{
                  ?concept skos:notation {notation} .
                  OPTIONAL {{
                    ?equipment dcterms:subject ?concept .
                    OPTIONAL {{ ?equipment oo:equipmentOf|oo:organizationPart|oo:formalOrganization|oo:formalOrganisation|foaf:based_near|spatialrelations:within|oo:availability ?other }}
                  }} .
                  OPTIONAL {{
                    ?concept skos:narrower ?narrower .
                    OPTIONAL {{ ?narrowerEquipment dcterms:subject ?narrower }}
                  }} .
                  OPTIONAL {{
                    ?broader skos:narrower ?concept .
                  }}
                }}""".format(notation=self.notation.n3())
        else:
            return """
                CONSTRUCT {{
                 {concept_scheme} a skos:ConceptScheme ;
                    skos:prefLabel ?conceptSchemeLabel ;
                    skos:hasTopConcept ?concept .
                  ?narrower a skos:Concept ;
                    skos:prefLabel ?conceptLabel ;
                    skos:notation ?conceptNotation ;
                    skos:narrower ?evenNarrower .
                }} WHERE {{
                  {concept_scheme} a skos:ConceptScheme ;
                    skos:prefLabel ?conceptSchemeLabel ;
                    skos:hasTopConcept ?concept .
                  ?concept skos:narrower* ?narrower .
                  ?narrower a skos:Concept ;
                    skos:prefLabel ?conceptLabel ;
                    skos:notation ?conceptNotation .
                  EXISTS {{
                    ?narrower skos:narrower*/^dcterms:subject ?equipment 
                  }} .
                  OPTIONAL {{
                    ?narrower skos:narrower ?evenNarrower .
                    EXISTS {{
                      ?evenNarrower skos:narrower*/^dcterms:subject ?narrowerEquipment
                    }}
                  }}
                }}""".format(concept_scheme=self.concept_scheme.n3())

    def finalize_context(self, request, context, notation):
        self.undefer()
        graph = context['_graph']
        context['equipment'] = list(map(self.resource, set(graph.subjects(NS.rdf.type, NS.oo.Equipment)) \
                                                     | set(graph.subjects(NS.rdf.type, NS.cerif.Equipment))))
        context['equipment'].sort(key=lambda s:s.label)
        if self.notation:
            concept = graph.value(None, NS.skos.notation, self.notation)
            if not concept:
                raise Http404
            context['concept'] = self.resource(concept)
            context['concepts'] = list(map(self.resource, graph.objects(concept, NS.skos.narrower)))
            context['level'] = 'subcategory' if '/' in self.notation else 'category'
        else:
            context['concepts'] = list(map(self.resource, graph.objects(self.concept_scheme, NS.skos.hasTopConcept)))
            context['level'] = 'index'
        context['concepts'].sort(key=lambda s:s.label)

        return context

class FacilityListView(EquipmentView, CannedQueryView, HTMLView, RDFView, MappingView):
    query = """
        DESCRIBE ?facility WHERE {
          VALUES ?facilityType { cerif:Facility oo:Facility } .
          ?facility a ?facilityType ;
            oo:formalOrganization <http://oxpoints.oucs.ox.ac.uk/id/00000000> ;
            oo:organizationPart ?organizationPart .
        }
    """

    template_name = "equipment/facilities"
    with_labels = True

    def get_subjects(self, graph):
        return set(graph.subjects(NS.rdf.type, NS.cerif.Facility)) \
             | set(graph.subjects(NS.rdf.type, NS.oo.Facility))

class LastIssuedView(EquipmentView, CannedQueryView, HTMLView, RDFView, MappingView):
    equipment_subset_uri = rdflib.URIRef('https://data.ox.ac.uk/id/dataset/research-facilities/equipment')
    query = """
        DESCRIBE ?subset WHERE {
          %(uri)s void:subset ?subset .
          ?subset oo:organizationPart ?organization ;
            dcterms:issued ?issued .
        }
    """ % {'uri': equipment_subset_uri.n3()}

    template_name = "equipment/last-issued"

    def get_subjects(self, graph):
        return graph.subjects(NS.rdf.type, NS.cat.Catalog)

    def sort_subjects(self, subjects):
        subjects.sort(key=lambda catalog: catalog.oo_organizationPart.label)
