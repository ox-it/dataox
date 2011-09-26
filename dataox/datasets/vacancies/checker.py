# -*- coding: utf-8 -*-
from __future__ import with_statement

import datetime

from humfrey.update.longliving.definitions import Definitions
from humfrey.update.longliving.updater import Updater
from humfrey.update.transform.base import Transform

from dataox.datasets.vacancies.recruitox import RecruitOxScraper

class RetrieveVacanciesChecker(Transform):
    COUNT_KEY = 'dataox:transform:vacancies:count'

    def execute(self, transform_manager):
        client = self.get_redis_client()
        params = RecruitOxScraper.search_params.copy()
        params['p_start_from'] = '0'
        html = RecruitOxScraper.get_html(RecruitOxScraper.search_url, params)
        
        pagination = html.xpath(".//span[@class='erq_searchv4_count']")[0].text.strip()
        pagination = RecruitOxScraper.search_pagination_re.match(pagination).groupdict()
        
        new_count = pagination['count']
        old_count = client.get(self.COUNT_KEY)

        if old_count is not None and old_count != new_count:
            self.queue_updater(client)
        
        client.set(self.COUNT_KEY, new_count)
    
    def queue_updater(self, client):
        meta = self.unpack(client.hget(Definitions.META_NAME, 'vacancies'))
        client.rpush(Updater.QUEUE_NAME, self.pack({
            'config_filename': meta['filename'],
            'name': meta['name'],
            'trigger': 'checker',
            'queued_at': datetime.datetime.now(),
        }))