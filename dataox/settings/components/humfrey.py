
ENDPOINT_QUERY = 'http://localhost:3030/public/query'
ENDPOINT_GRAPH = 'http://localhost:3030/public/data'

HUMFREY_FEEDS = {
    'organization': 'dataox.feeds.organization.OrganizationFeedView',
}

UPDATE_TRANSFORMS = (
    'dataox.vacancy.transform.RetrieveVacancies',
    'dataox.vacancy.transform.RetrieveVacanciesChecker',
    'dataox.oxpoints.transform.extents.OxpointsExtents',
    'humfrey.update.transform.base.Requires',
    'humfrey.update.transform.construct.Construct',
    'humfrey.update.transform.html.HTMLToXML',
    'humfrey.update.transform.normalize.Normalize',
    'humfrey.update.transform.retrieve.Retrieve',
    'humfrey.update.transform.sharepoint.SharePoint',
    'humfrey.update.transform.shell.Shell',
    'humfrey.update.transform.spreadsheet.GnumericToTEI',
    'humfrey.update.transform.spreadsheet.ODSToTEI',
    'humfrey.update.transform.spreadsheet.CSVToTEI',
    'humfrey.update.transform.union.Union',
    'humfrey.update.transform.upload.Upload',
    'humfrey.update.transform.vocabularies.VocabularyLoader',
    'humfrey.update.transform.xslt.XSLT',
)

RESOURCE_REGISTRY = 'dataox.resource.resource_registry'

ID_MAPPING = (
    ('https://data.ox.ac.uk/id/equipment/', 'https://www.research-facilities.ox.ac.uk/view:equipment/', True),
    ('https://data.ox.ac.uk/id/facility/', 'https://www.research-facilities.ox.ac.uk/view:facility/', True),
    ('https://data.ox.ac.uk/id/', 'https://data.ox.ac.uk/doc/', True),
    ('http://oxpoints.oucs.ox.ac.uk/id/', 'https://data.ox.ac.uk/doc:oxpoints/', False),
    ('http://id.it.ox.ac.uk/', 'https://data.ox.ac.uk/doc:it/', True),
    ('http://id.conted.ox.ac.uk/', 'https://course.data.ox.ac.uk/doc:conted/', False),
)

HTML_MIMETYPES = ('application/xhtml+xml', 'text/html')

ID_MAPPING_REDIRECTS = (
    ('http://id.conted.ox.ac.uk/course/(?P<id>.*)', 'http://www.conted.ox.ac.uk/courses/details.php?id=%(id)s', HTML_MIMETYPES),
    ('http://id.conted.ox.ac.uk/presentation/(?P<id>.*)', 'http://www.conted.ox.ac.uk/%(id)s', HTML_MIMETYPES),
)

DOC_RDF_PROCESSORS = (
    'humfrey.desc.rdf_processors.doc_meta',
    'humfrey.desc.rdf_processors.formats',
)

IMAGE_PROPERTIES = ('foaf:depiction',)

ADDITIONAL_NAMESPACES = {
    'adhoc': 'http://vocab.ox.ac.uk/ad-hoc-data-ox/',
    'cerif': 'http://spi-fm.uca.es/neologism/cerif#',
    'exif': 'http://www.w3.org/2003/12/exif/ns#',
    'oosc': 'http://purl.org/openorg/space-configuration/',
    'prog': 'http://purl.org/prog/',
    'spatialrelations': 'http://data.ordnancesurvey.co.uk/ontology/spatialrelations/',
    'mlo' : 'http://purl.org/net/mlo/',
    'xcri': 'http://xcri.org/profiles/1.2/',
    'vacancy': 'http://purl.org/openorg/vacancy/',
    'meter': 'http://purl.org/meter/',
    'oxnotation': 'https://data.ox.ac.uk/id/notation/',
    'prog': 'http://purl.org/prog/',
    'oxcap': 'http://purl.ox.ac.uk/oxcap/ns/',
    'cat': 'http://purl.org/NET/catalog/',
}

ELASTICSEARCH_SERVER = {'host': 'localhost', 'port': 9200}

GRAPH_BASE = 'https://data.ox.ac.uk/graph/'

VOCABULARY_URL_OVERRIDES = {
    'afn': None,
    'cc': 'http://creativecommons.org/schema.rdf',
    'fn': None,
    'oxnotation': None,
    'oxp': 'http://oxpoints.oucs.ox.ac.uk/ns.ttl',
    'pf': None,
    'lyou': 'http://openorg.ecs.soton.ac.uk/linkingyou/linkingyou.ttl',
}

IMAGE_TYPES = ('foaf:Image',)

SOURCE_URL = 'https://source.data.ox.ac.uk/'

DEFAULT_STORE = 'public'

DEPENDENT_TASKS = {'humfrey.update.update': ('humfrey.ckan.upload_dataset_metadata',
                                             'humfrey.update.run_dependents',
                                             'humfrey.archive.update_dataset_archives',
                                             'humfrey.elasticsearch.update_indexes_after_dataset_update')}

DATASET_NOTATION = 'oxnotation:dataset'
