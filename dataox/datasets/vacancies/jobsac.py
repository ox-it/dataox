from .base import Scraper

class JobsAcScraper(Scraper):
    search_base_url = "http://www.jobs.ac.uk/employer/university-of-oxford/latest/page/"
    job_base_url = "http://www.jobs.ac.uk/job/"

    def get_vacancies(self, current_vacancies):
        pass
