import logging
import rdflib
import urllib2

from humfrey.sparql.endpoint import Endpoint
from humfrey.update.transform.base import Transform
from humfrey.utils.namespaces import NS

from lxml.builder import ElementMaker
from lxml import etree

logger = logging.getLogger(__name__)

GEOM = rdflib.Namespace('http://data.ordnancesurvey.co.uk/ontology/geometry/')
GML = "http://www.opengis.net/gml"

E = ElementMaker(namespace=GML, nsmap={'gml': GML})

class OxpointsExtents(Transform):
    query = """
    SELECT * WHERE {
        ?uri oxp:hasOSMIdentifier ?osm
    }
    """
    
    api_url = "http://api.openstreetmap.org/api/0.6/{type}/{id}"
    
    def execute(self, transform_manager):
        endpoint = Endpoint(transform_manager.store.query_endpoint)
        graph = rdflib.ConjunctiveGraph()
        results = endpoint.query(self.query)
        for result in results:
            osm_type, osm_id = result.osm.split('/')[:2]
            if osm_type != 'relation':
                continue
            url = self.api_url.format(type=osm_type, id=osm_id)
            if osm_type in ('way', 'relation'):
                url += '/full'
            print url
            
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                if e.code == 410:
                    logger.warning("OSM entity for %s, %s gone", result.uri, result.osm)
                else:
                    raise
                continue

            xml = etree.parse(response)
            process_func = getattr(self, 'process_{0}'.format(osm_type))
            process_func(graph, xml, osm_id, result.uri)
            
        with open(transform_manager('rdf'), 'w') as target:
            graph.serialize(target)
        
        return target.name
    
    def process_relation(self, graph, xml, osm_id, uri):
        relation = xml.xpath("/osm/relation[@id='{0}']".format(osm_id))[0]
        if not relation.xpath("tag[@k='type' and @v='multipolygon']"):
            logger.warning("Relation %s for %s is not of type multipolygon", osm_id, uri)
            return
        
        polygon = E('Polygon')
        for member in sorted(relation.xpath("member"), key=lambda m:m.attrib.get('role'), reverse=True):
            if member.attrib.get('type') != 'way':
                logger.warning("Member %s of relation %s for %s is not a way",
                               member.attrib.get('ref'), osm_id, uri)                
            if member.attrib.get('role') not in ('inner', 'outer'):
                logger.warning("Member %s of relation %s for %s is not inner or outer",
                               member.attrib.get('ref'), osm_id, uri)
                continue
            polygon.append(E('exterior' if member.attrib.get('role') == 'outer' else 'interior',
                             self.get_way_geom(xml, member.attrib['ref'])))
        self.create_geometry(graph, uri, polygon)
        
        print etree.tostring(polygon)#, pretty_print=True)
        
    
    def process_way(self, graph, xml, osm_id, uri):
        data = self.get_way_geom(xml, osm_id)
        if data.tag.endswith('}LinearRing'):
            data = E('Polygon', E('exterior', data))
        self.create_geometry(graph, uri, data)

    def process_node(self, graph, xml, osm_id, uri):
        node = xml.xpath("/osm/node[@id='{0}']".format(osm_id))[0]
        data = E('Point', E('pos',
                            '{lon} {lat}'.format(**node.attrib),
                            srsDimension='2'))
        self.create_geometry(graph, uri, data)

    def create_geometry(self, graph, uri, data):
        data.attrib['srsName'] = 'http://www.opengis.net/def/crs/EPSG/0/4326'
        geom = rdflib.URIRef('{0}/extent'.format(uri))
        graph += (
            (uri, GEOM.extent, geom),
            (geom, NS.rdf.type, GEOM.AbstractGeometry),
            (geom, GEOM.asGML, rdflib.Literal(etree.tostring(data), datatype=NS.rdf.XMLLiteral))
        )
        return geom

    def get_way_geom(self, xml, way_id):
        pos_list = []
        nds = xml.xpath("/osm/way[@id='{0}']/nd".format(way_id))
        for nd in nds:
            node = xml.xpath("/osm/node[@id='{0}']".format(nd.attrib['ref']))[0]
            pos_list.extend((node.attrib['lon'], node.attrib['lat']))

        
        pos_list = E('posList', ' '.join(pos_list), srsDimension='2')
        
        return E('LinearRing' if nds[0].attrib['ref'] == nds[-1].attrib['ref'] else 'LineString',
                 pos_list)
        

if __name__ == '__main__':
    from humfrey.sparql.models import Store
    transform = OxpointsExtents()
    tm = type('TransformManager', (object,), {})()
    tm.store = Store.objects.get(slug='public')
    transform.execute(tm)