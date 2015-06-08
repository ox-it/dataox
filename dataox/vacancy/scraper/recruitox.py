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
from django.db.models import Q
from lxml import etree
import pytz

from .base import Scraper
from ..models import Vacancy, Document

logger = logging.getLogger(__name__)

def _normalize_space(text):
    return ' '.join(text.split())

class RecruitOxScraper(Scraper):
    base_url = 'https://www.recruit.ox.ac.uk/pls/hrisliverecruit/'
    feed_url = urlparse.urljoin(base_url, 'Erq_search_xml_api.build_search_xml?p_internal_external=A&p_company=10')
    detail_url = urlparse.urljoin(base_url, 'erq_jobspec_version_4.display_form')

    site_timezone = pytz.timezone('Europe/London')

    detail_salary_re = re.compile(ur'^(Grade|Salary)[^\dA-Z]+(?P<grade>[^:]{,32})[-:][^£]*£? ?(?P<lower>[\d,]+)(?:[^£]*£ ?(?P<upper>[\d,]+)(?:[^£]+£(?P<discretionary>[\d,]+))?)?')

    category_mapping = {'AC': 'academic',
                        'ST': 'support-technical',
                        'TS': 'temporary-staffing-service',
                        'RE': 'research',
                        'PM': 'professional-management'}

    detail_params = {'p_company': '10',
                     'p_internal_external': 'E',
                     'p_display_in_irish': 'N',
                     'p_applicant_no': '',
                     'p_process_type': '',
                     'p_form_profile_detail': '',
                     'p_display_apply_ind': 'Y',
                     'p_refresh_search': 'Y'}

    @classmethod
    def get_page(cls, url, params=None, parser_cls=etree.HTMLParser):
        if params:
            url = '%s?%s' % (url, urllib.urlencode(params))
        request = urllib2.Request(url)
        request.headers['User-agent'] = cls.user_agent
        if cls.crawl_delay:
            time.sleep(cls.crawl_delay)
        return etree.parse(urllib2.urlopen(request),
                           parser=parser_cls(encoding="WINDOWS-1252"))

    def get_vacancy_elems(self):
        feed_xml = self.get_page(self.feed_url, parser_cls=etree.XMLParser)
        vacancy_elems = feed_xml.xpath('/currentVacancies/vacancy')
        for vacancy_elem in vacancy_elems:
            for elem in vacancy_elem:
                if elem.text:
                    elem.text = elem.text.strip('\n')
        return vacancy_elems

    @classmethod
    def normalize_space(self, text):
        return ' '.join(text.split()) if text else ''

    def import_vacancies(self):
        changed = False
        seen = set()
        for vacancy_elem in self.get_vacancy_elems():
            vacancy_id = vacancy_elem.find('recruitmentId').text
            try:
                changed = self.import_vacancy(vacancy_id, vacancy_elem) or changed
            except Exception:
                logger.exception("Unable to parse vacancy %r", vacancy_id)
            seen.add(vacancy_id)

        now = self.site_timezone.localize(datetime.datetime.now()).replace(microsecond=0)
        old = set(v.vacancy_id for v in Vacancy.objects.filter(Q(opening_date__lt=now.isoformat()),
                                                               Q(closing_date__isnull=True) | Q(closing_date__gt=now.isoformat())))
        logger.info("Added: %r; Removed: %r", sorted(seen - old), sorted(old - seen))

        # If vacancies have disappeared, say that they've just closed.
        for vacancy in Vacancy.objects.all():
            if vacancy.closing_date:
                closes = dateutil.parser.parse(vacancy.closing_date)
            else:
                closes = None
            if (not closes or closes > now) and vacancy.vacancy_id not in seen:
                logger.info("Vacancy %s has gone missing; closing. Expected end at %s",
                            vacancy.vacancy_id, vacancy.closing_date)
                vacancy.closing_date = now.isoformat()
                vacancy.save()
                changed = True

        return changed

    def get_description(self, vacancy_id, vacancy_elem):
        """
        Returns the description as an XHTML string.

        This handles line-breaks, turning them into <p> and <br> tags as
        appropriate, and removes @target attributes from links.
        """
        lines = (vacancy_elem.find('jobDescription').text or '').split('\n')
        description, in_p = ['<div>'], False
        for line in lines:
            if line:
                if in_p:
                    description.append("<br/>\n")
                else:
                    description.append('\n<p>')
                    in_p = True
                description.append(line.strip())
            elif in_p:
                description.append('</p>\n')
                in_p = False
        if in_p:
            description.append('</p>\n')
        description.append('</div>')

        try:
            # The HTMLParser wraps in /html/body if there isn't one already,
            # so we traverse down to our div element with [0][0]
            description = etree.fromstring(''.join(description),
                                           parser=etree.HTMLParser(encoding='WINDOWS-1252'))[0][0]
        except etree.ParseError:
            logger.exception("Failed to parse description for vacancy %s", vacancy_id)
            return None

        # Links seem to always come with @target="_blank", so let's get rid of that.
        for anchor in description.xpath('.//a[@target]'):
            del anchor.attrib['target']
        description.attrib['xmlns'] = 'http://www.w3.org/1999/xhtml'

        return etree.tostring(description)

    def get_parsed_date(self, dt):
        if not dt:
            return None
        # e.g. 29-MAY-2015 09:00
        dt = datetime.datetime.strptime(dt, '%d-%b-%Y %H:%M')
        return self.site_timezone.localize(dt).isoformat()

    def import_vacancy(self, vacancy_id, vacancy_elem):
        changed = False
        try:
            vacancy = Vacancy.objects.get(vacancy_id=vacancy_id)
        except Vacancy.DoesNotExist:
            vacancy = Vacancy(vacancy_id=vacancy_id)

        params = self.detail_params.copy()
        params['p_recruitment_id'] = vacancy_id
        vacancy.url = '%s?%s' % (self.detail_url, urllib.urlencode(params))

        vacancy.title = self.normalize_space(vacancy_elem.find('shortDescription').text)
        vacancy.salary = self.normalize_space(vacancy_elem.find('gradeAndSalaryText').text)

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

        vacancy.description = self.get_description(vacancy_id, vacancy_elem)

        vacancy.contact_name = self.normalize_space(vacancy_elem.find('contactPersonText').text)
        vacancy.contact_email = self.normalize_space(vacancy_elem.find('contactEmailText').text)
        vacancy.contact_phone = self.normalize_space(vacancy_elem.find('contactPhoneText').text)

        location =  self.normalize_space(vacancy_elem.find('orgGroupLocationText').text)
        if location != vacancy.location:
            vacancy.location = location
            vacancy.update_location_fields(self.transform_manager.store.slug,
                                           self.normalize_space(vacancy_elem.xpath('department/code')[0].text))

        vacancy.opening_date = self.get_parsed_date(vacancy_elem.find('externalOpenDateTime').text)
        vacancy.closing_date = self.get_parsed_date(vacancy_elem.find('externalCloseDateTime').text)

        vacancy.internal = 'INTERNAL APPLICANTS ONLY' in vacancy.description
        vacancy.tags = vacancy_elem.find('tagsText').text or ''

        category = (vacancy_elem.find('competitionType').find('code').text or '').strip()
        vacancy.category = self.category_mapping.get(category, '')

        if vacancy.is_dirty():
            changed = True
            vacancy.save()

        current_documents = dict((d.pk, d) for d in Document.objects.filter(vacancy=vacancy))
        for document_elem in vacancy_elem.xpath('documentLink'):
            url = urlparse.urljoin(self.detail_url,
                                   document_elem.find('documentURL').text.strip().replace(' ', '%20'))
            try:
                document = Document.objects.get(url=url, vacancy=vacancy)
            except Document.DoesNotExist:
                document = Document(url=url, vacancy=vacancy)
            document.title = (document_elem.find('documentName').text or '').strip()
            if document.title == '':
                logger.warning("File %s for vacancy %s has no title", url, vacancy_id)

            if document.is_dirty():
                changed = True
                document.save()
            current_documents.pop(document.pk, None)

        for document in current_documents.values():
            changed = True
            document.delete()

        return changed
