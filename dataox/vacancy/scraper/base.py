from humfrey.elasticsearch.query import ElasticSearchEndpoint
from humfrey.sparql.endpoint import Endpoint

class Scraper(object):
    user_agent = 'Mozilla/4.0 (compatible; University of Oxford Open Data; opendata@oucs.ox.ac.uk)'
    crawl_delay = 1

    def __init__(self, transform_manager):
        self.transform_manager = transform_manager
        self.sparql_endpoint = Endpoint(transform_manager.store.query_endpoint)
        self.search_endpoint = ElasticSearchEndpoint(transform_manager.store, 'organization')
