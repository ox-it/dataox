import base64
import datetime
import email.utils
import logging
import os
import pickle
import subprocess
import time
import urllib
import urllib2

from django.conf import settings
import pytz
import redis

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
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def convert_to_text(self, file_path, mimetype):
        if mimetype not in self.conversions:
            return NotImplemented
        filename = os.path.split(file_path)[-1]

        with open(file_path, 'rb') as f:
            request_mimetype, body = self.encode_multipart_formdata([], [('fileToConvert', filename, mimetype, f.read())])

        conversion_url = self.oxgarage_base + '/'.join(mt.replace('/', '%3A') for mt in self.conversions[mimetype])
        try:
            request = urllib2.Request(conversion_url, body)
            request.headers['Content-type'] = request_mimetype
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8')
        except urllib2.HTTPError:
            logger.exception("Couldn't convert %r using OxGarage", file_path)
            return ""

class PDFConverter(object):
    def convert_to_text(self, file_path, mimetype):
        if mimetype != 'application/pdf':
            return NotImplemented
        pdftotext = subprocess.Popen(['pdftotext', file_path, '-'], stdout=subprocess.PIPE)
        pdftotext.wait()
        return pdftotext.stdout.read().decode('utf-8')

class VacancyFileHandler(object):
    TEXT_HASH = 'dataox:transform:vacancies:file-texts'

    def __init__(self):
        self.converters = (OxGarageConverter(), PDFConverter())
        self.client = redis.client.Redis(**settings.REDIS_PARAMS)
    def pack(self, value):
        return base64.b64encode(pickle.dumps(value))
    def unpack(self, value):
        return pickle.loads(base64.b64decode(value))

    def retrieve_files(self, transform_manager, vacancy):
        file_path_base = os.path.join(settings.SOURCE_DIRECTORY, 'vacancies')
        file_url_base = transform_manager.parameters['file-url']

        for file in vacancy.files:
            filename = file['url'].split('/')[-1]
            file_path = os.path.join(file_path_base, vacancy.id.encode('utf-8'), filename)
            file_url = '%s%s/%s' % (file_url_base, vacancy.id, filename)

            file['local_url'] = file_url

            request = urllib2.Request(file['url'])
            request.get_method = lambda: 'HEAD'
            try:
                response = urllib2.urlopen(request)
            except urllib2.HTTPError:
                logger.exception("Error for HEAD request to %r", file['url'])
                continue

            file['mimetype'] = response.headers.get('Content-type')

            last_modified = self.parse_http_date(response.headers['Last-modified'])
            last_modified_ts = time.mktime(last_modified.timetuple())

            fetch_file = not os.path.exists(file_path) or os.stat(file_path).st_mtime < last_modified_ts

            if fetch_file:
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                urllib.urlretrieve(file['url'], file_path)
                os.utime(file_path, (last_modified_ts, last_modified_ts))

            if fetch_file or not self.client.hexists(self.TEXT_HASH, vacancy.id):
                for converter in self.converters:
                    text = converter.convert_to_text(file_path, file['mimetype'])
                    if text is not NotImplemented:
                        file['text'] = text.replace(u'\x0c', '') # Form-feeds are Baf
                        break
                else:
                    file['text'] = None
                self.client.hset(self.TEXT_HASH, vacancy.id, self.pack(file['text']))
            else:
                file['text'] = self.unpack(self.client.hget(self.TEXT_HASH, vacancy.id))


    def parse_http_date(self, ts):
        return pytz.utc.localize(datetime.datetime(*email.utils.parsedate(ts)[:7]))

