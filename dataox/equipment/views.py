import httplib
import urllib2
try:
    import json
except ImportError:
    import simplejson

from django_conneg.views import HTMLView, JSONPView
from django.conf import settings
from django.http import Http404

from humfrey.desc import views as desc_views
from humfrey.elasticsearch import views as elasticsearch_views
from humfrey.linkeddata.views import MappingView
from humfrey.results.views.standard import RDFView
from humfrey.sparql.views import StoreView

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
        print 'store', '{0}/equipment'.format(self.store_name)
        return '{0}/equipment'.format(self.store_name)

class DescView(EquipmentView, desc_views.DescView):
    pass

class DocView(EquipmentView, desc_views.DocView):
    template_name = 'equipment/view'

class SearchView(EquipmentView, elasticsearch_views.SearchView):
    facets = {'department': {'terms': {'field': 'equipmentOf.uri',
                                        'size': 20}},
              'basedNear': {'terms': {'field': 'basedNear.uri',
                                      'size': 20}}}
    
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

class BrowseView(HTMLView, RDFView, StoreView, MappingView):
    def get(self, request, notation):
        context = {'notation': notation}
        return self.render(request, context, 'equipment/browse')