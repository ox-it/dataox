# -*- coding: utf-8 -*-
import datetime
import itertools
import logging
import re
import time
import urllib
import urllib2
import urlparse

import dateutil.parser
from lxml import etree
import pytz

from .base import Scraper
from ..models import Vacancy, Document

logger = logging.getLogger(__name__)

def _normalize_space(text):
    return ' '.join(text.split())

class RecruitOxScraper(Scraper):
    base_url = 'https://www.recruit.ox.ac.uk/pls/hrisliverecruit/'
    site_timezone = pytz.timezone('Europe/London')
    COUNT_KEY = 'dataox:transform:vacancies:count'

    start_search_url = base_url + 'erq_search_package.search_form?p_company=10&p_internal_external=E'
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
    detail_salary_re = re.compile(ur'^(Grade|Salary)[^\dA-Z]+(?P<grade>[^:]{,32})[-:][^£]*£? ?(?P<lower>[\d,]+)(?:[^£]*£ ?(?P<upper>[\d,]+)(?:[^£]+£(?P<discretionary>[\d,]+))?)?')

    def __init__(self, transform_manager):
        self.quick = transform_manager.update_log.trigger == 'crontab'
        super(RecruitOxScraper, self).__init__(transform_manager)

    @classmethod
    def get_html(cls, url, params=None):
        if params:
            url = '%s?%s' % (url, urllib.urlencode(params))
        request = urllib2.Request(url)
        request.headers['User-agent'] = cls.user_agent
        if cls.crawl_delay:
            time.sleep(cls.crawl_delay)
        return etree.parse(urllib2.urlopen(request), parser=etree.HTMLParser(encoding="WINDOWS-1252"))

    def import_vacancies(self):
        changed = False

        if self.quick and not self.number_of_vacancies_changed():
            return changed
        
        departments = self.get_department_options()

        seen = set()
        for department in departments:
            vacancy_ids = self.get_vacancy_identifiers(department)
            seen.update(vacancy_ids)

            for vacancy_id in vacancy_ids:
                try:
                    changed = self.import_vacancy(vacancy_id, department) or changed
                except Exception:
                    logger.exception("Unable to parse vacancy %r", vacancy_id)

        now = self.site_timezone.localize(datetime.datetime.now()).replace(microsecond=0)
        now = now.isoformat()
        old = set(v.vacancy_id for v in Vacancy.objects.filter(opening_date__lt=now, closing_date__gt=now))
        logger.info("Added: %r; Removed: %r", seen - old, old - seen)


        # If vacancies have disappeared, say that they've just closed.
        now = self.site_timezone.localize(datetime.datetime.now()).replace(microsecond=0)
        for vacancy in Vacancy.objects.all():
            if vacancy.closing_date:
                closes = dateutil.parser.parse(vacancy.closing_date)
            else:
                closes = None
            if (not closes or closes > now) and vacancy.vacancy_id not in seen:
                vacancy.closing_date = now.isoformat()
                vacancy.save()
                changed = True
        
        return changed

    def number_of_vacancies_changed(self):
        params = self.search_params.copy()
        params['p_start_from'] = '0'
        html = self.get_html(RecruitOxScraper.search_url, params)

        pagination = html.xpath(".//span[@class='erq_searchv4_count']")[0].text.strip()
        pagination = self.search_pagination_re.match(pagination).groupdict()

        new_count = int(pagination['count'])

        now = self.site_timezone.localize(datetime.datetime.now()).replace(microsecond=0)
        now = now.isoformat()
        old_count = Vacancy.objects.filter(opening_date__lt=now, closing_date__gt=now).count()

        logger.debug("Expected vacancies: %d; Listed vacancies: %d", old_count, new_count)
        return new_count != old_count

    def get_department_options(self):
        html = self.get_html(self.start_search_url)
        options = html.xpath("//select[@name='p_department']/option")[1:]
        return [option.attrib['value'] for option in options]

    def get_vacancy_identifiers(self, department):
        vacancy_identifiers = set()
        for page_number in itertools.count():
            params = self.search_params.copy()
            params['p_start_from'] = page_number * 10
            params['p_department'] = department
            html = self.get_html(self.search_url, params)
            logger.info("Got page number %d", page_number)

            vacancy_identifiers.update(map(unicode, html.xpath(self.search_vacancy_identifier_xpath)))

            pagination = html.xpath(".//span[@class='erq_searchv4_count']")[0].text.strip()
            pagination = self.search_pagination_re.match(pagination).groupdict()
            if pagination['end'] == pagination['count']:
                break

        return vacancy_identifiers

    def import_vacancy(self, vacancy_id, department):
        changed = False

        try:
            vacancy = Vacancy.objects.get(vacancy_id=vacancy_id)
        except Vacancy.DoesNotExist:
            vacancy = Vacancy(vacancy_id=vacancy_id,
                              opening_date=self.site_timezone.localize(datetime.datetime.now()).replace(microsecond=0).isoformat())
        else:
            if self.quick and vacancy.last_checked and vacancy.last_checked + datetime.timedelta(1) > datetime.datetime.now():
                logger.debug("Ignoring vacancy %s", vacancy_id)
                return changed
        logger.info("Retrieving vacancy %s", vacancy_id)

        params = self.detail_params.copy()
        params['p_recruitment_id'] = vacancy_id
        html = self.get_html(self.detail_url, params)
        vacancy.url = '%s?%s' % (self.detail_url, urllib.urlencode(params))

        title_td = html.xpath(".//td[@class='erq_searchv4_heading1']")
        vacancy.title = ' '.join(title_td[0].text.split()) if title_td else ''

        salary_td = html.xpath(".//td[@class='erq_searchv4_heading3']")
        vacancy.salary =  ' '.join((salary_td[0].text or '').split()) if len(salary_td) == 2 else ''

        salary_match = self.detail_salary_re.match(vacancy.salary)
        if salary_match:
            salary = salary_match.groupdict()
            vacancy.salary_grade = salary.get('grade') or ''
            for k in ('lower', 'upper', 'discretionary'):
                if salary.get(k):
                    setattr(vacancy, 'salary_' + k, int(salary[k].replace(',', '')))
            vacancy.salary_upper = vacancy.salary_upper or vacancy.salary_lower
        else:
            vacancy.salary_lower, vacancy.salary_upper = None, None
            vacancy.salary_discretionary, vacancy.salary_grade = None, ''

        description = html.xpath(".//td[@class='erq_searchv4_heading3']")[-1]
        description.attrib.clear()
        description.tag = 'div'
        description.attrib['xmlns'] = 'http://www.w3.org/1999/xhtml'
        vacancy.description = etree.tostring(description)

        meta = dict(zip([_normalize_space(x.text) for x in html.xpath(".//*[@class='erq_searchv4_heading5_label']")],
                        html.xpath(".//*[@class='erq_searchv4_heading5_text']")))
        for key in meta:
            if len(meta[key]):
                meta[key] = meta[key][0].text
            else:
                meta[key] = meta[key].text

        vacancy.contact_name = meta.pop('Contact Person :', '') or ''
        vacancy.contact_email = meta.pop('Contact Email :', '') or ''
        vacancy.contact_phone = meta.pop('Contact Phone :', '') or ''

        location_td = html.xpath(".//td[@class='erq_searchv4_heading2']")
        location =  ' '.join(location_td[0].text.split()) if location_td else ''
        if location != vacancy.location:
            vacancy.location = location
            vacancy.update_location_fields(self.transform_manager.store.slug, department)

        closing_time = re.findall(r'\b(\d{1,2})[.:](\d{2})(?:\s*([ap]m))?\b', vacancy.description, re.I)
        if closing_time and not re.search('\W(noon|midday)\W', vacancy.description, re.I):
            closing_time = closing_time[-1]
            closing_hour, closing_minute, closing_am_pm = closing_time
            closing_hour, closing_minute = int(closing_hour), int(closing_minute)
            if (closing_am_pm or '').lower() == 'pm' and closing_hour < 12:
                closing_hour += 12
            if not (0 <= closing_hour <= 23 and 0 <= closing_minute <= 59):
                closing_hour, closing_minute = 12, 0
        else:
            closing_hour, closing_minute = 12, 0

        closing_date = meta.pop('Closing Date :')
        try:
            closing_date = datetime.datetime.strptime(closing_date, '%d-%b-%Y')
        except (TypeError, ValueError):
            logger.warning("Vacancy %s has no closing date", vacancy_id)
            vacancy.closing_date = None
        else:
            closing_date = closing_date.replace(hour=closing_hour, minute=closing_minute)
            vacancy.closing_date = self.site_timezone.localize(closing_date).replace(microsecond=0).isoformat()

        vacancy.internal = 'INTERNAL APPLICANTS ONLY' in vacancy.description

        meta.pop('Vacancy ID :')
        if meta:
            logger.warning("Extra metadata not parsed: %s", ', '.join(meta))

        if vacancy.is_dirty():
            vacancy.save()
            changed = True


        current_documents = {d.pk: d for d in Document.objects.filter(vacancy=vacancy)}
        for row in html.xpath(".//table[@class='erqlayouttable']//tr")[1:]:
            anchor = row.xpath('.//a')[0]
            url = urlparse.urljoin(self.detail_url, anchor.attrib['href'])

            try:
                document = Document.objects.get(url=url, vacancy=vacancy)
            except:
                document = Document(url=url, vacancy=vacancy)
            document.title = anchor.text or ''
            if document.title == '':
                logger.warning("File %s for vacancy %s has no title", url, vacancy_id)

            if document.is_dirty():
                document.save()
                changed = True
            current_documents.pop(document.pk, None)

        for document in current_documents:
            document.delete()

        return changed
