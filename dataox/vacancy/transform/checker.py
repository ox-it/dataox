# -*- coding: utf-8 -*-
from __future__ import with_statement

from humfrey.update.transform.base import Transform
from humfrey.update.models import UpdateDefinition

from dataox.vacancy.scraper import RecruitOxScraper

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
        UpdateDefinition.objects.get(slug='vacancies').queue()
