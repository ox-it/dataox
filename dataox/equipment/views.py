import httplib
import urllib2
try:
    import json
except ImportError:
    import simplejson

from django_conneg.views import HTMLView, JSONPView
from django.conf import settings
from django.http import Http404

from humfrey.elasticsearch import views as elasticsearch_views

class EquipmentView(object):
    """
    Mixin to choose between public and internal indexes.
    """

    @property
    def index_name(self):
        if self.request.user.groups.filter(name='member').count():
            return 'equipment/equipment'
        else:
            return 'public/equipment'
class SearchView(EquipmentView, elasticsearch_views.SearchView):
    facets = {'department': {'terms': {'field': 'equipmentOf.uri',
                                        'size': 20}},
              'basedNear': {'terms': {'field': 'basedNear.uri',
                                      'size': 20}}}
    
    template_name = 'equipment/search'

class ItemView(EquipmentView, HTMLView, JSONPView):
    def get(self, request, id):
        try:
            url = ('http://%(host)s:%(port)s/%s/' % (settings.ELASTICSEARCH_SERVER, self.index_name)) + id
            item = elasticsearch_views.SearchView.Deunderscorer(json.load(urllib2.urlopen(url)))
        except urllib2.HTTPError, e:
            if e.code == httplib.NOT_FOUND:
                raise Http404
            raise
        
        more_like_this_url = url + '/_mlt?min_doc_freq=1'
        
        context = {'item': item,
                   'more_like_this': elasticsearch_views.SearchView.Deunderscorer(json.load(urllib2.urlopen(more_like_this_url)))}
        
        return self.render(request, context, 'equipment/item')
        