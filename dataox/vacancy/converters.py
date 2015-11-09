import subprocess

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
