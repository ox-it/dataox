
class Scraper(object):
    user_agent = 'Mozilla/4.0 (compatible; University of Oxford Open Data; opendata@oucs.ox.ac.uk)'
    crawl_delay = 1

    def __init__(self, transform_manager):
        self.transform_manager = transform_manager
