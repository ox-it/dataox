import types

import dateutil.parser
import rdflib
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.utils.feedgenerator import RssUserland091Feed, Rss201rev2Feed, Atom1Feed, rfc2822_date

from django_conneg.decorators import renderer
from django_conneg.views import HTMLView, JSONPView, ContentNegotiatedView
from humfrey.utils.namespaces import NS
from humfrey.linkeddata.resource import Resource
from humfrey.results.views.standard import RDFView
from humfrey.sparql.views import CannedQueryView

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

    def simplify(self, value):
        if isinstance(value, Resource):
            return NotImplemented
        elif isinstance(value, rdflib.Literal) and value.datatype == NS.xsd.dateTime:
            return self.simplify(dateutil.parser.parse(value))
        elif isinstance(value, rdflib.Literal):
            value = value.toPython()
            if isinstance(value, rdflib.Literal):
                value = unicode(value)
            return self.simplify(value)
        elif isinstance(value, (rdflib.URIRef, rdflib.BNode)):
            return unicode(value)
        else:
            return super(FeedView, self).simplify(value)

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

class VacancyIndexView(HTMLView, CannedQueryView):
    query = """
      SELECT ?unit (SAMPLE(?unitLabel_) as ?unitLabel) (COUNT(DISTINCT ?vacancy) as ?vacancies) (SAMPLE(?subUnit_) as ?subUnit) WHERE {
        GRAPH <http://data.ox.ac.uk/graph/vocabulary/oxp> {
          ?type rdfs:subClassOf* org:Organization
        } .
        ?unit rdf:type ?type ; skos:prefLabel ?unitLabel_ .
        OPTIONAL { ?subUnit_ org:subOrganizationOf ?unit } .
        OPTIONAL {
          GRAPH <http://data.ox.ac.uk/graph/vacancies/current> {
            ?vacancy vacancy:organizationalUnit ?unit
          }
        }
      } GROUP BY ?unit ORDER BY ?unitLabel
    """
    template_name = "feeds/vacancy-index"

class VacancyView(FeedView, RDFView):
    template_name = "feeds/vacancy"
    _json_indent=2
    
    all = False
    
    @property
    def reverse_name(self):
        return 'feeds:all-vacancies' if self.all else 'feeds:vacancies'

    @property
    def query(self):
        return """
    DESCRIBE %%(unit)s ?unit ?vacancy ?salary WHERE {
      OPTIONAL {
        GRAPH <http://data.ox.ac.uk/graph/vacancies/current> {
          ?vacancy a vacancy:Vacancy ;
            vacancy:organizationalUnit ?unit ;
            vacancy:salary ?salary ;
            vacancy:applicationClosingDate ?closes ;
            rdfs:label ?label ;
            rdfs:comment ?description .
          FILTER (?closes > now()) .
        } .
        GRAPH <http://data.ox.ac.uk/graph/oxpoints> {
          ?unit org:subOrganizationOf%(cardinality)s %%(unit)s
        } .
        %%(filter)s
      }

    }""" % {'cardinality': '*' if self.all else '{0}'}

    def get(self, request, oxpoints_id, format=None):
        filter = []
        if 'keyword' in request.GET:
            keyword = rdflib.Literal(request.GET['keyword']).n3()
            filter.append("FILTER (regex(?label, %(keyword)s, 'i') || regex(?description, %(keyword)s, 'i'))" % {'keyword': keyword})
        filter = ' .\n      '.join(filter)
        self.unit = rdflib.URIRef('http://oxpoints.oucs.ox.ac.uk/id/%s' % oxpoints_id)

        self.graph = self.endpoint.query(self.query % {'unit': self.unit.n3(), 'filter': filter})
        if not self.graph:
            raise Http404

        formats = {}
        for renderer in self._renderers:
            formats[renderer.format] = {'url': request.build_absolute_uri(reverse(self.reverse_name, args=[oxpoints_id, renderer.format])),
                                        'format': renderer.format,
                                        'name': renderer.name,
                                        'mimetypes': renderer.mimetypes}
            if request.META['QUERY_STRING']:
                formats[renderer.format]['url'] += '?' + request.META['QUERY_STRING']

        
        self.context = {'unit': Resource(self.unit, self.graph, self.endpoint),
                        'graph': self.graph,
                        'formats': formats.values(),
                        'format_mapping': formats,
                        'all': self.all,
                        'keyword': request.GET.get('keyword')}
        
        return super(VacancyView, self).get(request, oxpoints_id=oxpoints_id, format=format)
        
    @property
    def title(self):
        return "Vacancies within " + self.graph.value(self.unit, NS.skos.prefLabel)
    
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
            format = self.get_renderers(request)[0].format
        return (request.build_absolute_uri(reverse(self.reverse_name, args=[oxpoints_id])),
                request.build_absolute_uri(reverse(self.reverse_name, args=[oxpoints_id, format])))
