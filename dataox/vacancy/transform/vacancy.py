# -*- coding: utf-8 -*-
from __future__ import with_statement

import datetime
import logging

import dateutil.parser
from django.conf import settings
import pytz
from humfrey.update.transform.base import Transform
from humfrey.streaming.rdfxml import RDFXMLSink

from ..scraper import RecruitOxScraper, JobsAcScraper
from ..files import VacancyFileHandler
from ..models import Vacancy, Document

logger = logging.getLogger(__name__)

class RetrieveVacancies(Transform):
    vacancy_base_uri = 'https://data.ox.ac.uk/id/vacancy/'

    site_timezone = pytz.timezone(settings.TIME_ZONE)


    #save_directory = "c:\\documents and settings\\orie2163\\my documents\\python\\jobs\\"
    #job_directory = "c:\\documents and settings\\orie2163\\my documents\\python\\jobs\\%s\\"

    def __init__(self, current_transform, archive_transform):
        self.current_transform = current_transform
        self.archive_transform = archive_transform

        self.scrapers = (RecruitOxScraper, JobsAcScraper)
        self.file_handler = VacancyFileHandler()

    def execute(self, transform_manager):
        scrapers = [scraper(transform_manager) for scraper in self.scrapers]
        
        logger.debug("Importing vacancies")

        for scraper in scrapers:
            scraper.import_vacancies()
            
        documents = Document.objects.filter(local_url='').select_related('vacancy')
        logger.debug("Finished importing vacancies; retrieving %d new documents", documents.count())
        file_handler = VacancyFileHandler()
        for document in documents:
            file_handler.retrieve(document)
        
        logger.debug("Finished retrieving documents; starting to serialize")

        transforms = {'current': {'file': open(transform_manager('rdf'), 'w'),
                                  'transform': self.current_transform},
                      'archive': {'file': open(transform_manager('rdf'), 'w'),
                                  'transform': self.archive_transform}}

        for transform in transforms.values():
            transform['sink'] = RDFXMLSink(transform['file'])
            transform['sink'].start()
        
        for vacancy in Vacancy.objects.all():
            opening_date, closing_date = map(dateutil.parser.parse, (vacancy.opening_date, vacancy.closing_date))
            if opening_date < self.site_timezone.localize(datetime.datetime.now()) < closing_date:
                transform = transforms['current']
            else:
                transform = transforms['archive']
            transform['sink'].triples(vacancy.triples(self.vacancy_base_uri))
        
        for name, transform in transforms.items():
            transform['sink'].end()
            logger.debug("Finished serializing %s graph (%d bytes)", name, transform['file'].tell())
            transform['file'].close()
            
            transform['transform'].execute(transform_manager, transform['file'].name)
