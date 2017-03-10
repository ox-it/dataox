import logging
import rdflib
import time
import urllib.request

from humfrey.sparql.endpoint import Endpoint
from humfrey.update.transform.base import Transform
from humfrey.utils.namespaces import NS
from lxml import etree
from osgeo import ogr

logger = logging.getLogger(__name__)

GEOM = rdflib.Namespace('http://data.ordnancesurvey.co.uk/ontology/geometry/')

class OxpointsExtents(Transform):
    query = """
    SELECT * WHERE {
        ?uri oxp:hasOSMIdentifier ?osm
    }
    """

    api_url = "http://api.openstreetmap.org/api/0.6/{type}/{id}"

    def __init__(self):
        self.processors = {'node': self.process_node,
                           'way': self.process_way,
                           'relation': self.process_relation}
        return super(OxpointsExtents, self).__init__()

    def union(self, geoms):
        geom = geoms[0]
        for g in geoms[1:]:
            geom = geom.Union(g)
        return geom

    def execute(self, transform_manager):
        endpoint = Endpoint(transform_manager.store.query_endpoint)
        graph = self.get_graph(endpoint)

        with open(transform_manager('rdf'), 'w') as target:
            graph.serialize(target)

        return target.name

    def get_graph(self, endpoint):
        graph = rdflib.ConjunctiveGraph()

        for uri, osms in endpoint.query(self.query):
            geoms = []
            for osm in osms.split():
                try:
                    osm_type, osm_id = osm.split('/')[:2]
                except ValueError:
                    logger.warning("OSM entity for %s, %s is malformed", uri, osm)
                    break
                url = self.api_url.format(type=osm_type, id=osm_id)
                if osm_type in ('way', 'relation'):
                    url += '/full'

                try:
                    response = urllib.request.urlopen(url)
                    time.sleep(0.25)
                except urllib.request.HTTPError as e:
                    if e.code == 410:
                        logger.warning("OSM entity for %s, %s gone", uri, osm)
                    elif e.code == 404:
                        logger.warning("OSM entity for %s, %s not found", uri, osm)
                    else:
                        raise
                    break
                except urllib.request.URLError:
                    logger.exception("URL error")
                    break

                xml = etree.parse(response)
                geom = self.processors[osm_type](xml, osm_id, uri)
                if not geom:
                    break
                geoms.append(geom)
            else:
                geom = self.union(geoms)
                extent = uri + '/extent'
                graph += [
                    (uri, GEOM.extent, extent),
                    (extent, NS.rdf.type, GEOM.AbstractGeometry),
                    (extent, GEOM.asGML, rdflib.Literal(geom.ExportToGML(), datatype=NS.rdf.XMLLiteral)),
                    (extent, GEOM.asWKT, rdflib.Literal(geom.ExportToWkt())),
                    (extent, GEOM.asGeoJSON, rdflib.Literal(geom.ExportToJson(), datatype=NS.xtypes['Fragment-JSON'])),
                    (extent, GEOM.asKML, rdflib.Literal(geom.ExportToKML(), datatype=NS.rdf.XMLLiteral)),
                ]
        return graph

    def process_relation(self, xml, osm_id, uri):
        relation = xml.xpath("/osm/relation[@id='{0}']".format(osm_id))[0]
        if not relation.xpath("tag[@k='type' and @v='multipolygon']"):
            logger.warning("Relation %s for %s is not of type multipolygon", osm_id, uri)
            return

        outers, inners = [], []
        for member in sorted(relation.xpath("member"), key=lambda m:m.attrib.get('role'), reverse=True):
            if member.attrib.get('type') != 'way':
                logger.warning("Member %s of relation %s for %s is not a way",
                               member.attrib.get('ref'), osm_id, uri)
            if member.attrib.get('role') not in ('inner', 'outer'):
                logger.warning("Member %s of relation %s for %s is not inner or outer",
                               member.attrib.get('ref'), osm_id, uri)
                continue

            way = self.process_way(xml, member.attrib['ref'], uri)
            if member.attrib.get('role') == 'outer':
                outers.append(way)
            else:
                inners.append(way)

        geom = self.union(outers)
        for inner in inners:
            geom = geom.Difference(inner)

        return geom

    def process_way(self, xml, way_id, uri):
        nds = xml.xpath("/osm/way[@id='{0}']/nd".format(way_id))
        ring = nds[0].attrib['ref'] == nds[-1].attrib['ref']
        geom = ogr.Geometry(ogr.wkbLinearRing if ring else ogr.wkbLineString)
        for nd in nds:
            node = xml.xpath("/osm/node[@id='{0}']".format(nd.attrib['ref']))[0]
            geom.AddPoint(float(node.attrib['lon']), float(node.attrib['lat']))
        if ring:
            polygon = ogr.Geometry(ogr.wkbPolygon)
            polygon.AddGeometry(geom)
            return polygon
        else:
            return geom

    def process_node(self, xml, node_id, uri):
        node = xml.xpath("/osm/node[@id='{0}']".format(node_id))[0]
        geom = ogr.Geometry(ogr.wkbPoint)
        geom.AddPoint(float(node.attrib['lon']), float(node.attrib['lat']))
        return geom

if __name__ == '__main__':
    transform = OxpointsExtents()
    endpoint = Endpoint('https://data.ox.ac.uk/sparql/')
    graph = transform.get_graph(endpoint)
    print(graph.serialize(format='turtle'))

