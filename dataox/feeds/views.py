import types

import dateutil.parser
import rdflib
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.utils.feedgenerator import RssUserland091Feed, Rss201rev2Feed, Atom1Feed, rfc2822_date
from django.shortcuts import render_to_response
from django.template import RequestContext

from django_conneg.decorators import renderer
from django_conneg.views import HTMLView, JSONPView, ContentNegotiatedView
from humfrey.utils.namespaces import NS
from humfrey.linkeddata.resource import Resource, BaseResource
from humfrey.linkeddata.views import MappingView
from humfrey.results.views.standard import RDFView, ResultSetView
from humfrey.sparql.views import CannedQueryView, StoreView

class IndexView(HTMLView):
    def get(self, request):
        return self.render(request, {}, 'feeds/index')

class FeedView(HTMLView, JSONPView):
    title = None
    link = None
    description = None
    template_name = None
    context = {}
    
    def get(self, request, *args, **kwargs):
        self.base_location, self.content_location = self.get_locations(request, *args, **kwargs)
        
        context = self.context.copy()
        context.update({'title': self.title,
                        'link': self.link,
                        'description': self.description,
                        'items': self.items})
        
        if self.content_location:
            context['additional_headers'] = {'Content-location': self.content_location}
        
        if kwargs.get('format'):
            return self.render_to_format(request, context, self.template_name, kwargs['format'])
        else: 
            return self.render(request, context, self.template_name)

    @renderer(format='rss1', mimetypes=('application/rss+xml',), name='RSS 0.9 Feed')
    def render_rss1(self, request, context, template_name):
        return self.renderGeneralFeed(request, context, RssUserland091Feed, 'application/rss+xml')    
    
    @renderer(format='rss', mimetypes=('application/rss+xml',), name='RSS 2.01 Feed')
    def render_rss2(self, request, context, template_name):
        return self.renderGeneralFeed(request, context, Rss201rev2Feed, 'application/rss+xml')
    
    @renderer(format='atom', mimetypes=('application/atom+xml',), name='Atom Feed')
    def render_atom(self, request, context, template_name):
        return self.renderGeneralFeed(request, context, Atom1Feed, 'application/atom+xml')
    
    def renderGeneralFeed(self, request, context, feed_class, mimetype):
        feed = feed_class(context['title'],
                          context['link'],
                          context['description'])

        feed.add_root_elements = types.MethodType(add_root_elements, feed)
        #setattr(feed, add_root_elements.__name__, types.MethodType(add_root_elements, feed))

        for item in context['items']:
            feed.add_item(item['title'], item['link'], item['description'], pubdate=item['date'])
        return HttpResponse(feed.writeString('utf-8'), mimetype=mimetype)

    def simplify_for_json(self, value):
        if isinstance(value, BaseResource):
            return value.uri
        elif isinstance(value, rdflib.Literal) and value.datatype == NS.xsd.dateTime:
            return self.simplify_for_json(dateutil.parser.parse(value))
        elif isinstance(value, rdflib.Literal):
            value = value.toPython()
            if isinstance(value, rdflib.Literal):
                value = unicode(value)
            return self.simplify_for_json(value)
        elif isinstance(value, (rdflib.URIRef, rdflib.BNode)):
            return unicode(value)
        else:
            return super(FeedView, self).simplify_for_json(value)

# This is a nasty workaround for the (known) bug in Django: 
# https://code.djangoproject.com/ticket/14202
# This is the troublesome method with a correction, 
# and must be assigned to the relevant feed class before use! 
def add_root_elements(self, handler):
    handler.addQuickElement(u"title", self.feed['title'])
    handler.addQuickElement(u"link", self.feed['link'])
    handler.addQuickElement(u"description", self.feed['description'])
    # handler.addQuickElement(u"atom:link", None, {u"rel": u"self", u"href": self.feed['feed_url']})
    if self.feed['language'] is not None:
        handler.addQuickElement(u"language", self.feed['language'])
    for cat in self.feed['categories']:
        handler.addQuickElement(u"category", cat)
    if self.feed['feed_copyright'] is not None:
        handler.addQuickElement(u"copyright", self.feed['feed_copyright'])
    handler.addQuickElement(u"lastBuildDate", rfc2822_date(self.latest_post_date()).decode('utf-8'))
    if self.feed['ttl'] is not None:
        handler.addQuickElement(u"ttl", self.feed['ttl'])        

class VacancyIndexView(CannedQueryView, ResultSetView):
    query = """
      SELECT ?unit (SAMPLE(?unitLabel_) as ?unitLabel) (COUNT(DISTINCT ?vacancy) as ?vacancies) (SAMPLE(?subUnit_) as ?subUnit) WHERE {
        ?type rdfs:subClassOf* org:Organization
        GRAPH <https://data.ox.ac.uk/graph/oxpoints/data> {
            ?unit rdf:type ?type ; skos:prefLabel ?unitLabel_ .
        }
        OPTIONAL { ?subUnit_ org:subOrganizationOf ?unit } .
        OPTIONAL {
          GRAPH <https://data.ox.ac.uk/graph/vacancies/current> {
            ?vacancy oo:organizationPart ?unit
          }
        }
      } GROUP BY ?unit ORDER BY ?unitLabel
    """
    template_name = "feeds/vacancy-index"

class VacancyView(FeedView, RDFView, StoreView, MappingView):
    template_name = "feeds/vacancy"
    _json_indent=2

    all = False

    @property
    def reverse_name(self):
        return 'feeds:all-vacancies' if self.all else 'feeds:vacancies'

    @property
    def query(self):
        return """\
CONSTRUCT {{
  ?vacancy a ?vacancyType ;
    rdfs:label ?vacancyLabel ;
    rdfs:comment ?vacancyComment ;
    skos:notation ?vacancyNotation ;
    vacancy:salary ?salary ;
    dc:spatial ?spatial ;
    vacancy:applicationOpeningDate ?opening ;
    vacancy:applicationClosingDate ?closing ;
    oo:formalOrganization ?formalOrganization ;
    oo:organizationPart ?organizationPart ;
    foaf:based_near ?location ;
    foaf:homepage ?homepage ;
    oo:contact ?contact .
  ?salary a ?salaryType ;
    rdfs:label ?salaryLabel ;
    gr:hasMinCurrencyValue ?salaryLower ;
    gr:hasMaxCurrencyValue ?salaryUpper ;
    gr:hasCurrency ?salaryCurrency ;
    adhoc:salaryGrade ?salaryGrade .
  ?organizationPart a ?organizationType ;
    rdfs:label ?organizationLabel ;
    rdfs:comment ?organizationComment ;
    v:adr ?organizationAddress ;
    foaf:homepage ?organizationHomepage ;
    skos:notation ?organizationNotation .
  ?location a ?locationType ;
    rdfs:label ?locationLabel ;
    v:adr ?locationAddress ;
    skos:notation ?locationNotation ;
    geo:lat ?locationLat ; geo:long ?locationLong .
  ?address a ?addressType ;
    v:street-address ?streetAddress ;
    v:extended-address ?extendedAddress ;
    v:locality ?locality ;
    v:postal-code ?postalCode .
  ?contact a ?contactType ;
    rdfs:label ?contactLabel ;
    v:email ?contactEmail ;
    v:tel ?phone .
  ?phone a ?phoneType ;
    rdfs:label ?phoneLabel ;
    rdf:value ?phoneValue .
}} WHERE {{
  VALUES ?unit {{ {unit} }} .
  ?organizationPart org:subOrganizationOf{cardinality} ?unit .
  OPTIONAL {{ ?organizationPart a ?organizationType }}
  OPTIONAL {{ ?organizationPart dc:title ?organizationLabel }}
  OPTIONAL {{ ?organizationPart skos:notation ?organizationNotation }}
  OPTIONAL {{ ?organizationPart v:adr ?organizationAddress }}
  OPTIONAL {{ ?organizationPart foaf:homepage ?organizationHomepage }}
  OPTIONAL {{
    GRAPH <https://data.ox.ac.uk/graph/vacancies/current> {{
      ?vacancy oo:organizationPart ?organizationPart ; a vacancy:Vacancy .
    }}
    ?vacancy vacancy:applicationClosingDate ?closing .
    FILTER (?closing > now()) .
    OPTIONAL {{ ?vacancy a ?vacancyType }}
    OPTIONAL {{ ?vacancy rdfs:label ?vacancyLabel }}
    OPTIONAL {{ ?vacancy rdfs:comment ?vacancyComment }}
    OPTIONAL {{ ?vacancy skos:notation ?vacancyNotation }}
    OPTIONAL {{ ?vacancy vacancy:salary ?salary }}
    OPTIONAL {{ ?vacancy dc:spatial ?spatial }}
    OPTIONAL {{ ?vacancy vacancy:applicationOpeningDate ?opening }}
    OPTIONAL {{ ?vacancy oo:formalOrganization ?formalOrganization }}
    OPTIONAL {{ ?vacancy oo:organizationPart ?organizationPart }}
    OPTIONAL {{ ?vacancy foaf:based_near ?location }}
    OPTIONAL {{ ?vacancy foaf:homepage ?homepage }}
    OPTIONAL {{ ?vacancy oo:contact ?contact }}
    {sparqlFilter}

    OPTIONAL {{ ?salary a ?salaryType }}
    OPTIONAL {{ ?salary rdfs:label ?salaryLabel }}
    OPTIONAL {{ ?salary gr:hasMinCurrencyValue ?salaryLower }}
    OPTIONAL {{ ?salary gr:hasMaxCurrencyValue ?salaryUpper }}
    OPTIONAL {{ ?salary gr:hasCurrency ?salaryCurrency }}
    OPTIONAL {{ ?salary adhoc:salaryGrade ?salaryGrade }}

    OPTIONAL {{ ?location a ?locationType }}
    OPTIONAL {{ ?location dc:title ?locationLabel }}
    OPTIONAL {{ ?location v:adr ?locationAddress }}
    OPTIONAL {{ ?location skos:notation ?locationNotation }}
    OPTIONAL {{ ?location geo:lat ?locationLat ; geo:long ?locationLong }}

    OPTIONAL {{ ?contact a ?contactType }}
    OPTIONAL {{ ?contact rdfs:label ?contactLabel }}
    OPTIONAL {{ ?contact v:email ?contactEmail }}
    OPTIONAL {{
      ?contact v:tel ?phone
      OPTIONAL {{ ?phone a ?phoneType }}
      OPTIONAL {{ ?phone rdfs:label ?phoneLabel }}
      OPTIONAL {{ ?phone rdf:value ?phoneValue }}
    }}

    OPTIONAL {{
      ?vacancy (oo:organizationPart|foaf:based_near)/v:adr ?address .
      ?address a ?addressType ;
      OPTIONAL {{ ?address v:street-address ?streetAddress }}
      OPTIONAL {{ ?address v:extended-address ?extendedAddress }}
      OPTIONAL {{ ?address v:locality ?locality }}
      OPTIONAL {{ ?address v:postal-code ?postalCode }}
    }}
    FILTER (BOUND(?vacancy) || ?unit = ?organizationPart)
  }}
}}""".format(cardinality='*' if self.all else '{0}',
             unit=self.unit.n3(),
             sparqlFilter=self.sparqlFilter)

    @property
    def unit(self):
        return rdflib.URIRef('http://oxpoints.oucs.ox.ac.uk/id/{0}'.format(self.kwargs['oxpoints_id']))

    @property
    def sparqlFilter(self):
        if 'keyword' in self.request.GET:
            keyword = rdflib.Literal(self.request.GET['keyword']).n3()
            return "FILTER (regex(?vacancyLabel, %(keyword)s, 'i') || regex(?vacancyComment, {0}, 'i'))".format(keyword)
        return ""

    def get(self, request, oxpoints_id, format=None):
        self.graph = self.endpoint.query(self.query)
        print self.query
        if not self.graph:
            raise Http404

        subjects = [Resource(v, self.graph, self.endpoint) for v in self.graph.subjects(NS.rdf.type, NS.vacancy.Vacancy)]

        self.context.update({'unit': Resource(self.unit, self.graph, self.endpoint),
                             'graph': self.graph,
                             'all': self.all,
                             'subjects': subjects,
                             'keyword': request.GET.get('keyword'),
                             'vacancies': []})

        for subject in subjects:
            if hasattr(subject, 'get_json'):
                self.context['vacancies'].append(subject.get_json())

        return super(VacancyView, self).get(request, oxpoints_id=oxpoints_id, format=format)

    @property
    def title(self):
        return "Vacancies within {0}".format(self.graph.value(self.unit, NS.rdfs.label) or '[unknown]')

    @property
    def link(self):
        return self.base_location

    @property
    def items(self):
        items = []
        for vacancy in self.graph.subjects(NS.rdf.type, NS.vacancy.Vacancy):
            descriptions = list(self.graph.objects(vacancy, NS.rdfs.comment))
            # Favour XHTML
            descriptions.sort(key=lambda description: description.datatype!=NS.xtypes['Fragment-XHTML'])
            resource = Resource(vacancy, self.graph, self.endpoint)
            items.append({'title': self.graph.value(vacancy, NS.rdfs.label),
                          'description': descriptions[0] if descriptions else None,
                          'link': self.graph.value(vacancy, NS.foaf.homepage),
                          'date': dateutil.parser.parse(self.graph.value(vacancy, NS.vacancy.applicationClosingDate)),
                          'pubdate': dateutil.parser.parse(self.graph.value(vacancy, NS.vacancy.applicationClosingDate)),
                          'resource': resource,
                          'unique_id': resource.hexhash})
            if self.all and resource.get('oo:organizationalUnit'):
                subdepts = [r.label for r in resource.get_all('oo:organizationalUnit') if r.get('skos:prefLabel') and r._identifier != self.unit]
                if subdepts:
                    items[-1]['title'] += " (%s)" % ', '.join(subdepts)
        items.sort(key=lambda item: (item['pubdate'], item['title']))
        return items

    def get_locations(self, request, oxpoints_id, format=None):
        if not format:
            format = request.renderers[0].format
        return (request.build_absolute_uri(reverse(self.reverse_name, args=[oxpoints_id])),
                request.build_absolute_uri(reverse(self.reverse_name, args=[oxpoints_id, format])))

    def url_for_format(self, request, format):
        return reverse(self.reverse_name, args=[self.kwargs['oxpoints_id'], format])

    @renderer(format='xml', mimetypes=('application/xml', 'text/xml'), name='XML')
    def render_xml(self, request, context, template_name):
        template_name = self.join_template_name(template_name, 'xml')
        return render_to_response(template_name,
                          context, context_instance=RequestContext(request),
                          mimetype='application/xml')
