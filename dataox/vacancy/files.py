from __future__ import with_statement

import base64
import datetime
import email.utils
import logging
import os
import pickle
import shutil
import subprocess
import time
import urllib2
import urlparse

from django.conf import settings
import pytz
import redis

from humfrey.update.tasks.retrieve import retrieve

logger = logging.getLogger(__name__)

class OxGarageConverter(object):
    oxgarage_base = 'http://oxgarage.oucs.ox.ac.uk:8080/ege-webservice/Conversions/'

    conversions = {
        'application/msword': ('doc/application/msword', 'txt/text/plain'),
        'application/vnd.openxmlformats': ('docx/application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'txt/text/plain'),
        'application/rtf': ('rtf/application/rtf', 'txt/text/plain'),
    }

    def encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, mimetype, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % mimetype)
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        print map(type, L)
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def convert_to_text(self, file_path, mimetype):
        if mimetype not in self.conversions:
            return NotImplemented
        filename = os.path.split(file_path)[-1]

        with open(file_path, 'rb') as f:
            request_mimetype, body = self.encode_multipart_formdata([], [('fileToConvert', filename.encode('utf8'), mimetype.encode('utf8'), f.read())])

        conversion_url = self.oxgarage_base + '/'.join(mt.replace('/', '%3A') for mt in self.conversions[mimetype])
        try:
            request = urllib2.Request(conversion_url, body)
            request.headers['Content-type'] = request_mimetype
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8', 'ignore')
        except urllib2.HTTPError:
            logger.exception("Couldn't convert %r using OxGarage", file_path)
            return ""

class PDFConverter(object):
    def convert_to_text(self, file_path, mimetype):
        if mimetype != 'application/pdf':
            return NotImplemented
        pdftotext = subprocess.Popen(['pdftotext', file_path, '-'], stdout=subprocess.PIPE)
        pdftotext.wait()
        return pdftotext.stdout.read().decode('utf-8', 'ignore')

class VacancyFileHandler(object):
    TEXT_HASH = 'dataox:transform:vacancies:file-texts'

    def __init__(self):
        self.converters = (OxGarageConverter(), PDFConverter())
    def pack(self, value):
        return base64.b64encode(pickle.dumps(value))
    def unpack(self, value):
        return pickle.loads(base64.b64decode(value))

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

        for converter in self.converters:
            try:
                text = converter.convert_to_text(file_path, document.mimetype)
            except Exception:
                logger.exception("Failed to convert %r (%r) to text using %s",
                                 document.url, document.mimetype, converter.__class__.__name__)
                continue
            if text is not NotImplemented:
                for x in u'\x04\x05\x0c':
                    text = text.replace(x, '')
                document.text = text
                break
        else:
            document.text = ''
        
        document.save()


    def parse_http_date(self, ts):
        return pytz.utc.localize(datetime.datetime(*email.utils.parsedate(ts)[:7]))

