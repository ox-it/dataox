from __future__ import with_statement

import datetime
import email.utils
import logging
import os
import re
import shutil
import subprocess
import time
import urlparse

from django.conf import settings
import pytz

from humfrey.update.tasks.retrieve import retrieve

logger = logging.getLogger(__name__)


class UNOConverter(object):
    def convert_to_text(self, file_path, mimetype):
        unoconv = subprocess.Popen(['unoconv', '--stdout', '-f', 'txt', file_path], stdout=subprocess.PIPE)
        text = []
        for line in unoconv.stdout:
            text.append(line)
        text = ''.join(text).decode('utf-8', 'ignore')
        # The replacement is to work around an OpenOffice/LibreOffice bug:
        # https://bugs.freedesktop.org/show_bug.cgi?id=51905
        text = text.replace(u'\x1e', u'\N{NON-BREAKING HYPHEN}')
        return text

class PDFConverter(object):
    def convert_to_text(self, file_path, mimetype):
        if mimetype != 'application/pdf':
            return NotImplemented
        pdftotext = subprocess.Popen(['pdftotext', file_path, '-'], stdout=subprocess.PIPE)
        text = []
        for line in pdftotext.stdout:
            text.append(line)
        text = ''.join(text).decode('utf-8', 'ignore')
        return text

converters = {
    'application/pdf': PDFConverter,
    'application/msword': UNOConverter,
    'application/vnd.openxmlformats': UNOConverter,
    'application/rtf': UNOConverter,
}

class VacancyFileHandler(object):
    def retrieve(self, document):
        file_path_base = os.path.join(settings.SOURCE_DIRECTORY, 'vacancies')
        file_url_base = urlparse.urljoin(settings.SOURCE_URL, 'vacancies/')

        filename = document.url.split('/')[-1]
        file_path = os.path.join(file_path_base, document.vacancy.vacancy_id.encode('utf-8'), filename)
        file_url = '%s%s/%s' % (file_url_base, document.vacancy.vacancy_id, filename)

        document.local_url = file_url

        logger.debug("Retrieving vacancy document: %s", document.url)
        filename, headers = retrieve(document.url)

        document.mimetype = headers.get('content-type')

        try:
            last_modified = self.parse_http_date(headers['last-modified'])
        except KeyError:
            pass
        else:
            last_modified_ts = time.mktime(last_modified.timetuple())
            os.utime(filename, (last_modified_ts, last_modified_ts))

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        shutil.copy2(filename, file_path)

        try:
            converter = converters[document.mimetype]()
        except KeyError:
            logger.warning("Unsupported mimetype for conversion '%s' for file %s",
                           document.mimetype, document.local_url)
            document.text = ''
        else:
            try:
                text = converter.convert_to_text(file_path, document.mimetype)
                logger.debug("Converted")
            except Exception:
                logger.exception("Failed to convert %r (%r) to text using %s",
                                 document.url, document.mimetype, converter.__class__.__name__)
                document.text = ''
            else:
                text = re.sub(ur'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff]', '', text)
                document.text = text
        
        document.save()
        
        return True

    def parse_http_date(self, ts):
        return pytz.utc.localize(datetime.datetime(*email.utils.parsedate(ts)[:7]))

