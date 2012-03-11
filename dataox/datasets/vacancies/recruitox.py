# -*- coding: utf-8 -*-
import datetime
import itertools
import logging
import re
import time
import urllib
import urllib2
import urlparse

from lxml import etree
import pytz

from .base import Scraper
from .vacancy import Vacancy

logger = logging.getLogger(__name__)

class RecruitOxScraper(Scraper):
    base_url = 'https://www.recruit.ox.ac.uk/pls/hrisliverecruit/'
    site_timezone = pytz.timezone('Europe/London')

    search_url = base_url + 'erq_search_version_4.start_search_with_params'
    search_params = {'p_company': '10',
                     'p_internal_external': 'E',
                     'p_display_in_irish': 'N',
                     'p_recruitment_id': '',
                     'p_competition_type': 'ALLOPTIONS',
                     'p_department': 'ALLOPTIONS',
                     'p_keywords': '',
                     'p_search_company': '',
                     'p_position': '',
                     'p_position_type': '',
                     'p_management_unit': '',
                     'p_description': '',
                     'p_location': '',
                     'p_division': '',
                     'p_pay_scale': '',
                     'p_force_type': 'E'}
    search_vacancy_identifier_xpath = ".//td[@class='erq_searchv4_result_row']//td[@class='erq_searchv4_heading5_text'][position()=1]/text()"
    search_pagination_re = re.compile(r'^Displaying (?P<start>\d+) to (?P<end>\d+) of (?P<count>\d+)')

    detail_url = base_url + 'erq_jobspec_version_4.display_form'
    detail_params = {'p_company': '10',
                     'p_internal_external': 'E',
                     'p_display_in_irish': 'N',
                     'p_applicant_no': '',
                     'p_process_type': '',
                     'p_form_profile_detail': '',
                     'p_display_apply_ind': 'Y',
                     'p_refresh_search': 'Y'}
    detail_salary_re = re.compile(ur'^(Grade|Salary)[^\dA-Z]+(?P<grade>[^:]+)[-:][^£]*£ ?(?P<lower>[\d,]+)(?:[^£]*£ ?(?P<upper>[\d,]+)(?:[^£]+£(?P<discretionary>[\d,]+))?)?')

    def get_vacancies(self, current_vacancies):
        vacancy_identifiers = self.get_vacancy_identifiers()

        for vacancy_id in vacancy_identifiers:
            try:
                current_vacancies[vacancy_id] = self.get_vacancy(vacancy_id)
            except Exception:
                logger.exception("Unable to parse vacancy %r", vacancy_id)

    @classmethod
    def get_html(cls, url, params):
        url = '%s?%s' % (url, urllib.urlencode(params))
        request = urllib2.Request(url)
        request.headers['User-agent'] = cls.user_agent
        if cls.crawl_delay:
            time.sleep(cls.crawl_delay)
        return etree.parse(urllib2.urlopen(request), parser=etree.HTMLParser(encoding="WINDOWS-1252"))

    def get_vacancy_identifiers(self):
        vacancy_identifiers = set()
        for page_number in itertools.count():
            params = self.search_params.copy()
            params['p_start_from'] = page_number * 10
            html = self.get_html(self.search_url, params)

            vacancy_identifiers.update(map(unicode, html.xpath(self.search_vacancy_identifier_xpath)))

            pagination = html.xpath(".//span[@class='erq_searchv4_count']")[0].text.strip()
            pagination = self.search_pagination_re.match(pagination).groupdict()
            if pagination['end'] == pagination['count']:
                break
        return vacancy_identifiers

    def get_vacancy(self, vacancy_id):
        logger.debug("Retrieving vacancy %r", vacancy_id)
        vacancy = Vacancy(vacancy_id)
        params = self.detail_params.copy()
        params['p_recruitment_id'] = vacancy_id
        html = self.get_html(self.detail_url, params)
        vacancy.url = '%s?%s' % (self.detail_url, urllib.urlencode(params))

        meta = html.xpath(".//td[@class='erq_searchv4_heading5_text']|.//td[@class='erq_searchv4_heading2']|.//td[@class='erq_searchv4_heading1']|.//td[@class='erq_searchv4_heading3']|.//td[@class='erq_border_bottom_dash_right']")
        meta = [(m, ' '.join((m.text or '').split())) for m in meta]
        vacancy.title = meta[0][1]

        salary = self.detail_salary_re.match(meta[2][1])
        if salary:
            vacancy.salary = salary.groupdict()
            for k in ('lower', 'upper', 'discretionary'):
                if vacancy.salary.get(k):
                    vacancy.salary[k] = int(vacancy.salary[k].replace(',', ''))
            vacancy.salary['upper'] = vacancy.salary['upper'] or vacancy.salary['lower']
        else:
            vacancy.salary = None
        if meta[2][1].startswith('Grade') or meta[2][1].startswith('Salary'):
            if not vacancy.salary:
                logger.warning("Couldn't parse salary for %s: %r", vacancy_id, meta[2][1])
            meta[2:3] = []


        description = meta[2][0]
        description.attrib.clear()
        description.tag = 'div'
        vacancy.description = etree.tostring(description)

        vacancy.contact = {}
        if meta[3][1]:
            vacancy.contact['name'] = meta[3][1]
        if meta[5][1]:
            vacancy.contact['phone'] = meta[5][1]
        if meta[7][0].xpath('.//a/@href'): # There's a mailto: URI
            vacancy.contact['email'] = unicode(meta[7][0].xpath('.//a/@href')[0]).split('?')[0]

        vacancy.location = meta[1][1]
        vacancy.roots, vacancy.orgparts = self.location_guesser.guess(vacancy.location, vacancy.description, None)

        vacancy.closes = datetime.datetime.strptime(meta[6][1], '%d-%b-%Y').replace(hour=12)
        vacancy.closes = self.site_timezone.localize(vacancy.closes)
        vacancy.previous_closes = []

        vacancy.internal = 'INTERNAL APPLICANTS ONLY' in vacancy.description

        vacancy.files = []
        for row in html.xpath(".//table[@class='erqlayouttable']//tr")[1:]:
            anchor = row.xpath('.//a')[0]
            file_url = urlparse.urljoin(self.detail_url, anchor.attrib['href'])
            vacancy.files.append({'url': file_url,
                                  'title': anchor.text})

        return vacancy
