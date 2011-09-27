from __future__ import with_statement

import imp
try:
    import json
except ImportError:
    import simplejson as json
import os

import unittest2

from dataox.datasets.vacancies.location import LocationGuesser

class TestLocationGuesser(LocationGuesser):
    data_directory = os.path.join(imp.find_module('dataox')[1],
                                  'resources', 'tests', 'vacancies')

    def get_parents(self):
        with open(os.path.join(self.data_directory, 'parents.json')) as f:
            return json.load(f)
    def get_query_results(self):
        with open(os.path.join(self.data_directory, 'query_results.json')) as f:
            query_results = json.load(f)
            query_results = dict((k, dict((k2, set(v2)) for k2, v2 in v.iteritems())) for k, v in query_results.iteritems())
            return query_results
    def get_expected(self):
        with open(os.path.join(self.data_directory, 'expected.json')) as f:
            return json.load(f)





class LocationTestCase(unittest2.TestCase):
    def testSimple(self):
        guesser = TestLocationGuesser()

        for location, expected in sorted(guesser.get_expected().iteritems()):
            if expected == 'failure':
                continue

            _, orgparts = guesser.guess(location, None, None)
            orgparts = sorted(map(unicode, orgparts))
            self.assertEqual(orgparts, expected, "%r > %r != %r" % (location,
                                                                    map(guesser.get_names, orgparts),
                                                                    map(guesser.get_names, expected or [])))


if __name__ == '__main__':
    unittest2.main()
