# -*- coding: utf-8 -*-
from __future__ import with_statement

import datetime
import email.utils
import itertools
import logging
import os
import re
import time
import urllib
import urllib2
import urlparse

from django.conf import settings
from lxml import etree
import pytz
import rdflib
from humfrey.update.transform.base import Transform
from humfrey.utils.namespaces import NS

from .vacancy import Vacancy
from .location import LocationGuesser
from .recruitox import RecruitOxScraper
from .jobsac import JobsAcScraper
from .files import VacancyFileHandler

logger = logging.getLogger(__name__)

class RetrieveVacancies(Transform):
    VACANCY_HASH = 'dataox:transform:vacancies:details'

    vacancy_base_uri = 'http://data.ox.ac.uk/id/vacancy/'

    site_timezone = pytz.timezone(settings.TIME_ZONE)


    #save_directory = "c:\\documents and settings\\orie2163\\my documents\\python\\jobs\\"
    #job_directory = "c:\\documents and settings\\orie2163\\my documents\\python\\jobs\\%s\\"

    def __init__(self, current_transform, removed_transform):
        self.current_transform = current_transform
        self.removed_transform = removed_transform

        self.scrapers = (RecruitOxScraper(), JobsAcScraper())
        self.file_handler = VacancyFileHandler()

    def execute(self, transform_manager):
        client = self.get_redis_client()

        run_started = self.site_timezone.localize(datetime.datetime.now()).replace(microsecond=0)

        current_vacancies = {}
        for scraper in self.scrapers:
            scraper.get_vacancies(current_vacancies)

        for vacancy_id in current_vacancies:
            vacancy = current_vacancies[vacancy_id]

            old_vacancy = client.hget(self.VACANCY_HASH, vacancy_id)
            old_vacancy = self.unpack(old_vacancy) if old_vacancy else None

            vacancy.created = getattr(old_vacancy, 'created', run_started)

            if vacancy != old_vacancy:
                vacancy.modified = run_started
            if old_vacancy and vacancy.closes != old_vacancy.closes:
                vacancy.previous_closes.append((run_started, old_vacancy.closes))

            self.file_handler.retrieve_files(transform_manager, vacancy)

        removed_vacancies = []
        for vacancy_id in client.hkeys(self.VACANCY_HASH):
            if vacancy_id not in current_vacancies:
                removed_vacancies.append(self.unpack(client.hget(self.VACANCY_HASH, vacancy_id)))

        onward_transforms = [(current_vacancies, self.current_transform, True),
                             (removed_vacancies, self.removed_transform, False)]

        for vacancies, transform, save in onward_transforms:
            graph = rdflib.ConjunctiveGraph()
            for vacancy_id in vacancies:
                vacancy = vacancies[vacancy_id]
                if save:
                    client.hset(self.VACANCY_HASH, vacancy.id, self.pack(vacancy))
                else:
                    client.hdel(self.VACANCY_HASH, vacancy.id)
                graph += vacancy.triples(self.vacancy_base_uri)
            with open(transform_manager('rdf'), 'w') as output:
                graph.serialize(output)
            transform.execute(transform_manager, output.name)
