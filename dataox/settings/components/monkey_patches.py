import sys
import rdflib
import urllib2

if map(int, rdflib.__version__.split('.')[0]) < 3:
    from datetime import date, time, datetime
    l = sys.modules['rdflib.Literal']
    _XSD_NS = l._XSD_NS
    l._PythonToXSD = [
        (basestring, (None,None)),
        (float     , (None,_XSD_NS[u'float'])),
        (bool      , (lambda i:str(i).lower(),_XSD_NS[u'boolean'])),
        (int       , (None,_XSD_NS[u'integer'])),
        (long      , (None,_XSD_NS[u'long'])),
        (datetime  , (lambda i:i.isoformat(),_XSD_NS[u'dateTime'])),
        (date      , (lambda i:i.isoformat(),_XSD_NS[u'date'])),
        (time      , (lambda i:i.isoformat(),_XSD_NS[u'time'])),
    ]
    del date, datetime, time, l, _XSD_NS


# http://bugs.python.org/issue9639 (Python 2.6.6 regression)

if sys.version_info[:2] == (2, 6) and sys.version_info[2] >= 6:
    def fixed_http_error_401(self, req, fp, code, msg, headers):
        url = req.get_full_url()
        response = self.http_error_auth_reqed('www-authenticate',
                                          url, req, headers)
        self.retried = 0
        return response

    urllib2.HTTPBasicAuthHandler.http_error_401 = fixed_http_error_401

del rdflib, sys, urllib2
