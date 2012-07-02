from .base import Scraper

class JobsAcScraper(Scraper):
    search_base_url = "http://www.jobs.ac.uk/employer/university-of-oxford/latest/page/"
    job_base_url = "http://www.jobs.ac.uk/job/"

    def import_vacancies(self):
        pass
