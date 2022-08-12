# -*- coding: utf-8 -*-
import datetime
import logging
import re
import time
import urllib.parse
import urllib.request
from io import BytesIO

import dateutil.parser
from django.db.models import Q
from lxml import etree
import pytz

from .base import Scraper
from ..models import Vacancy, Document

from humfrey.elasticsearch.query import ElasticSearchEndpoint

logger = logging.getLogger(__name__)


def _normalize_space(text):
    return ' '.join(text.split())


class RecruitOxScraper(Scraper):
    base_url = 'https://my.corehr.com/pls/uoxrecruit/'
    feed_url = urllib.parse.urljoin(base_url, 'Erq_search_xml_api.build_search_xml?p_internal_external=A&p_company=10')
    detail_url = urllib.parse.urljoin(base_url, 'erq_jobspec_version_4.display_form')

    site_timezone = pytz.timezone('Europe/London')

    old_salary_re = re.compile(r'^(Grade|Salary)[^\dA-Z]+(?P<grade>[^:]{,32})[-:][^£]*£? ?(?P<lower>[\d,]+)(?:[^£]*£ ?(?P<upper>[\d,]+)(?:[^£]+£(?P<discretionary>[\d,]+))?)?')
    new_salary_re = re.compile(r'^(\d+) - (\d+)')

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
            url = '%s?%s' % (url, urllib.parse.urlencode(params))
        request = urllib.request.Request(url)
        request.headers['User-agent'] = cls.user_agent
        if cls.crawl_delay:
            time.sleep(cls.crawl_delay)
        response = urllib.request.urlopen(request)
        # Hack because the next v20 of CoreHR adds leading whitespace to the XML feed.
        if parser_cls == etree.XMLParser:
            response = BytesIO(response.read().strip())
        return etree.parse(response,
                           parser=parser_cls(encoding="utf-8"))

    def get_vacancy_elems(self):
        feed_xml = self.get_page(self.feed_url, parser_cls=etree.XMLParser)
        vacancy_elems = feed_xml.xpath('/currentVacancies/vacancy')
        for vacancy_elem in vacancy_elems:
            for elem in vacancy_elem:
                if elem.text:
                    elem.text = elem.text.strip('\n')
                    elem.text = elem.text.strip('\r')
                    elem.text = elem.text.strip('\f')
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
        old = set(v.vacancy_id
                  for v in Vacancy.objects.filter(Q(opening_date__lt=now.isoformat()),
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
                                           parser=etree.HTMLParser(encoding='utf-8'))[0][0]
        except etree.ParseError:
            logger.exception("Failed to parse description for vacancy %s", vacancy_id)
            return None

        # Links seem to always come with @target="_blank", so let's get rid of that.
        for anchor in description.xpath('.//a[@target]'):
            del anchor.attrib['target']
        description.attrib['xmlns'] = 'http://www.w3.org/1999/xhtml'

        return etree.tostring(description).decode()

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
        vacancy.url = '%s?%s' % (self.detail_url, urllib.parse.urlencode(params))

        page = self.get_page(vacancy.url)

        vacancy.title = self.normalize_space(vacancy_elem.find('shortDescription').text)
        
        grade_and_salary_text = self.normalize_space(vacancy_elem.find('gradeAndSalaryText').text)
        old_salary_match = self.old_salary_re.match(grade_and_salary_text)
        new_salary_match = self.new_salary_re.match(grade_and_salary_text)

        # The salary text matches the old format
        # e.g. "Grade 7: £33,309 - £40,927 p.a."
        if old_salary_match:
            salary = old_salary_match.groupdict()
            vacancy.salary = grade_and_salary_text
            vacancy.salary_grade = salary.get('grade') or ''
            for k in ('lower', 'upper', 'discretionary'):
                if salary.get(k):
                    setattr(vacancy, 'salary_' + k, int(salary[k].replace(',', '')))
            vacancy.salary_upper = vacancy.salary_upper or vacancy.salary_lower
        # The salary text matches the new format
        # e.g. "33309 - 44706"
        elif new_salary_match:
            pay_scale = self.normalize_space(vacancy_elem.xpath('payScale/description')[0].text)
            pay_scale = pay_scale.title()
            salary = new_salary_match.groups()
            vacancy.salary_lower = salary[0]
            lower_string = "£" + "{:,}".format(int(vacancy.salary_lower))
            vacancy.salary_upper = salary[1]
            upper_string = "£" + "{:,}".format(int(vacancy.salary_upper))
            if pay_scale:
                vacancy.salary = pay_scale + ': ' + lower_string + ' - ' + upper_string
            else:
                vacancy.salary = lower_string + ' - ' + upper_string
            vacancy.salary_discretionary, vacancy.salary_grade = None, ''
        # gradeAndSalaryText element is empty
        elif grade_and_salary_text == '':
            vacancy.salary = ''
            vacancy.salary_lower, vacancy.salary_upper = None, None
            vacancy.salary_discretionary, vacancy.salary_grade = None, ''
        # The salary matches neither standard format and isn't empty,
        # so assume it is free text
        else:
            pay_scale = self.normalize_space(vacancy_elem.xpath('payScale/description')[0].text)
            pay_scale = pay_scale.title()
            if pay_scale:
                vacancy.salary = pay_scale + ': ' + grade_and_salary_text
            else:
                vacancy.salary = grade_and_salary_text
            vacancy.salary_lower, vacancy.salary_upper = None, None
            vacancy.salary_discretionary, vacancy.salary_grade = None, ''

        vacancy.description = self.get_description(vacancy_id, vacancy_elem)

        vacancy.contact_name = self.normalize_space(vacancy_elem.find('contactPersonText').text)
        vacancy.contact_email = self.normalize_space(vacancy_elem.find('contactEmailText').text)
        vacancy.contact_phone = self.normalize_space(vacancy_elem.find('contactPhoneText').text)

        department_code = self.normalize_space(vacancy_elem.xpath('department/code')[0].text)
        search_endpoint = ElasticSearchEndpoint(self.transform_manager.store.slug, 'organization')
        
        if department_code:
            # We have to insert a special case here for the Department of Biology.
            # For a while now, new entities haven't been getting imported into Elasticsearch,
            # and it's too difficult to fix, so we've left it.
            # Biology is a new department and thus not in Elasticsearch, so the code below this
            # can't find it, and vacancies don't get associated with it when they should be.
            # Unfortunately the only way to fix this is to hard code it like this.
            if department_code == 'CB':
                department = 'http://oxpoints.oucs.ox.ac.uk/id/50814249'
            else:
                results = search_endpoint.query({'query': {'term': {'finance': department_code}}})
                try:
                    department = results['hits']['hits'][0]['_source']['uri']
                except (IndexError, KeyError):
                    logger.error("Couldn't find department for code %s", department_code)
                    department = None

        location =  self.normalize_space(vacancy_elem.find('orgGroupLocationText').text)
        if (location != vacancy.location) or ((department) and (vacancy.organizationPart != department)):
            vacancy.location = location
            vacancy.update_location_fields(self.transform_manager.store.slug,
                                           self.normalize_space(department))

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
        for i, anchor_elem in enumerate(page.xpath("//*[@class='erqanchor8point']")):
            url = urllib.parse.urljoin(self.detail_url,
                                       anchor_elem.attrib['href'].replace(' ', '%20'))
            try:
                document = Document.objects.get(index=i,
                                                title=(anchor_elem.text or '').strip(),
                                                vacancy=vacancy)
            except Document.DoesNotExist:
                document = Document(index=i,
                                    title=(anchor_elem.text or '').strip(),
                                    vacancy=vacancy)
            if document.title == '':
                logger.warning("File %d for vacancy %s has no title", i, vacancy_id)

            document.ensure_present(url)

            if document.is_dirty():
                changed = True
                document.save()
            current_documents.pop(document.pk, None)

        for document in current_documents.values():
            changed = True
            document.delete()

        return changed
