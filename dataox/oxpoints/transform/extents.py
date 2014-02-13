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
            try:
                osm_type, osm_id = result.osm.split('/')[:2]
            except ValueError:
                logger.warning("OSM entity for %s, %s is malformed", result.uri, result.osm)
                continue
            url = self.api_url.format(type=osm_type, id=osm_id)
            if osm_type in ('way', 'relation'):
                url += '/full'

            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                if e.code == 410:
                    logger.warning("OSM entity for %s, %s gone", result.uri, result.osm)
                elif e.code == 404:
                    logger.warning("OSM entity for %s, %s not found", result.uri, result.osm)
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
        wkts = {'outer': [], 'inner': []}
        for member in sorted(relation.xpath("member"), key=lambda m:m.attrib.get('role'), reverse=True):
            if member.attrib.get('type') != 'way':
                logger.warning("Member %s of relation %s for %s is not a way",
                               member.attrib.get('ref'), osm_id, uri)
            if member.attrib.get('role') not in ('inner', 'outer'):
                logger.warning("Member %s of relation %s for %s is not inner or outer",
                               member.attrib.get('ref'), osm_id, uri)
                continue

            nodes, ring = self.get_nodes(xml, member.attrib['ref'])
            polygon.append(E('exterior' if member.attrib.get('role') == 'outer' else 'interior',
                             self.get_way_geom(nodes, ring)))
            way_wkt = '({0})'.format(', '.join(' '.join(node) for node in nodes))
            wkts[member.attrib.get('role')].append(way_wkt)

        if len(wkts['outer']) > 1 and len(wkts['inner']) == 0:
            wkt = 'MULTIPOLYGON({0})'.format(', '.join('({0})'.format(w) for w in wkts['outer']))
        elif len(wkts['outer']) == 1:
            wkt = 'POLYGON({0}, {1})'.format(wkts['outer'][0],
                                             ', '.join(wkts['inner']))
        else:
            wkt = None
            logger.warning("Not clever enough to serialize WKT for " +
                           "multipolygon with {0} outer(s) and {1} " +
                           "inner(s)".format(len(wkts['outer']), len(wkts['inner'])))

        self.create_geometry(graph, uri, polygon, wkt)

    def process_way(self, graph, xml, osm_id, uri):
        nodes, ring = self.get_nodes(xml, osm_id)
        data = self.get_way_geom(nodes, ring)
        if ring:
            data = E('Polygon', E('exterior', data))
        wkt = '{0}(({1}))'.format('POLYGON' if ring else 'LINESTRING',
                                ', '.join(' '.join(node) for node in nodes))
        self.create_geometry(graph, uri, data, wkt)

    def process_node(self, graph, xml, osm_id, uri):
        node = xml.xpath("/osm/node[@id='{0}']".format(osm_id))[0]
        data = E('Point', E('pos',
                            '{lon} {lat}'.format(**node.attrib),
                            srsDimension='2'))
        wkt = "POINT({lon} {lat})".format(**node.attrib)
        self.create_geometry(graph, uri, data, wkt)

    def create_geometry(self, graph, uri, data, wkt=None):
        data.attrib['srsName'] = 'http://www.opengis.net/def/crs/EPSG/0/4326'
        geom = rdflib.URIRef('{0}/extent'.format(uri))
        graph += (
            (uri, GEOM.extent, geom),
            (geom, NS.rdf.type, GEOM.AbstractGeometry),
            (geom, GEOM.asGML, rdflib.Literal(etree.tostring(data), datatype=NS.rdf.XMLLiteral))
        )
        if wkt:
            graph.add((geom, GEOM.asWKT, rdflib.Literal(wkt)))
        return geom

    def get_way_geom(self, nodes, ring):
        pos_list = E('posList', ' '.join(' '.join(node) for node in nodes), srsDimension='2')
        return E('LinearRing' if ring else 'LineString',
                 pos_list)

    def get_nodes(self, xml, way_id):
        nodes = []
        nds = xml.xpath("/osm/way[@id='{0}']/nd".format(way_id))
        for nd in nds:
            node = xml.xpath("/osm/node[@id='{0}']".format(nd.attrib['ref']))[0]
            nodes.append((node.attrib['lon'], node.attrib['lat']))
        return nodes, nds[0].attrib['ref'] == nds[-1].attrib['ref']

if __name__ == '__main__':
    from humfrey.sparql.models import Store
    transform = OxpointsExtents()
    tm = type('TransformManager', (object,), {})()
    tm.store = Store.objects.get(slug='public')
    transform.execute(tm)
