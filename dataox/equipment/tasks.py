import logging
import requests
import tempfile

from celery.task import task
from django.conf import settings
from humfrey.signals import graphs_updated
from humfrey.streaming.csv import CSVSerializer
from humfrey.utils.user_agents import USER_AGENTS
import rdflib

logger = logging.getLogger(__name__)

watch_graphs = frozenset(map(rdflib.URIRef, (
    'https://data.ox.ac.uk/graph/oxpoints/data',
    'https://data.ox.ac.uk/graph/oxpoints/metadata',
    'https://data.ox.ac.uk/graph/equipment/equipment',
    'https://data.ox.ac.uk/graph/equipment/facilities',
    'https://data.ox.ac.uk/graph/equipment/taxonomy',
)))

TARGET_URL = getattr(settings, 'SEESEC_TARGET_URL', None)
CREDENTIALS = getattr(settings, 'SEESEC_CREDENTIALS', (None, None))

query = """\
SELECT *
""" + '\n'.join("FROM " + wg.n3() for wg in watch_graphs) + """
WHERE {
  VALUES (?type ?rdf_type) {
    ("equipment" cerif:Equipment)
    ("equipment" oo:Equipment)
    ("facility" cerif:Facility)
    ("facility" oo:Facility)
  }
  ?id a ?rdf_type .
  OPTIONAL { ?id rdfs:label ?name }
  OPTIONAL { ?id rdfs:comment ?description }
  OPTIONAL { ?id oo:facility ?related_facility_id }
  OPTIONAL {
    ?id foaf:based_near/owl:sameAs? ?based_near
    FILTER regex(str(?based_near), "^http://dbpedia\\\\.org/resource/")
    BIND (uri(concat('http://en.wikipedia.org/wiki', substr(str(?based_near), 28))) AS ?location)
  }
  OPTIONAL { BIND (<http://en.wikipedia.org/wiki/Oxford> AS ?location) }
  OPTIONAL {
    {
      SELECT ?id (SAMPLE(?c) AS ?contact) {
        ?id a ?type
        OPTIONAL { ?id oo:primaryContact ?c }
        OPTIONAL { ?id oo:contact ?c }
        FILTER (BOUND(?c))
      } GROUP BY ?id
    }
    EXISTS { ?id oo:primaryContact|oo:contact ?contact }
    OPTIONAL { ?contact foaf:name ?contact_name }
    OPTIONAL { ?contact v:tel ?contact_telephone }
    OPTIONAL {
      ?contact v:email ?contact_mailto
      BIND(SUBSTR(STR(?contact_mailto), 8) AS ?contact_email)
    }
  }
  OPTIONAL { ?id foaf:img ?photo }
  OPTIONAL { ?id foaf:depiction ?photo }
  OPTIONAL { ?id oo:organizationPart/(skos:prefLabel|rdfs:label) ?organisational_unit }
  OPTIONAL { ?id foaf:based_near/(skos:prefLabel|rdfs:label) ?site_location }
  OPTIONAL { ?id spatialrelations:within/v:adr/v:locality ?site_location }
  OPTIONAL { BIND ("Oxford" AS ?site_location) }
  OPTIONAL { ?id spatialrelations:within/skos:prefLabel ?building }
  OPTIONAL { ?id foaf:page ?web_address }
  BIND ("ogl" AS ?open_license)
  FILTER(BOUND(?contact_name) && (BOUND(?contact_telephone) || BOUND(?contact_url) || BOUND(?contact_email)))
}
"""

@task(name='dataox.equipment.update_seesec', ignore_result=True)
def update_seesec(sender, store, graphs, when, **kwargs):
    if store.slug != 'seesec':
        return
    
    if not (watch_graphs & graphs):
        logger.debug("No SEESEC graphs updated; not updating")
        return 

    if not TARGET_URL:
        logger.debug("No SEESEC target URL set; not updating")
        return

    with tempfile.TemporaryFile() as f:
        for line in CSVSerializer(store.query(query)):
            f.write(line)

        content_length = f.tell()
        f.seek(0)
        logger.debug("Updating SEESEC (%d bytes)", content_length)

        response = requests.post(TARGET_URL,
                                 files={'file': f},
                                 data={'institution': 'oxford'},
                                 auth=CREDENTIALS,
                                 headers={'User-Agent': USER_AGENTS['agent']})
    if response.status_code != requests.codes.ok:
        logger.error("Failed to upload equipment to SEESEC (%d):\n\n%s",
                     response.status_code,
                     response.text)
    else:
        logger.info("Successfully uploaded equipment to SEESEC")

graphs_updated.connect(update_seesec.delay)

if __name__ == '__main__':
    from datetime import datetime
    from humfrey.sparql.models import Store
    logging.basicConfig(level=logging.DEBUG)

    update_seesec(None,
                    store=Store.objects.get(slug='seesec'),
                    graphs=set([rdflib.URIRef('https://data.ox.ac.uk/graph/equipment/facilities')]),
                    when=datetime.now())
