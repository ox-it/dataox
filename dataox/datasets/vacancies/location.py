import collections
import itertools
import logging
import operator
import re

import enchant
import rdflib


from django.conf import settings
from humfrey.utils.namespaces import NS
from humfrey.sparql.endpoint import Endpoint

logger = logging.getLogger(__name__)

class LocationGuesser(object):

    queries = {
        'org-name': """
        SELECT ?thing ?label WHERE {
            ?thing rdf:type/rdfs:subClassOf* org:Organization ;
                skos:prefLabel|skos:altLabel|skos:hiddenLabel ?label . 
        }""",
        'place-name': """
        SELECT ?thing ?label WHERE {
            ?thing org:hasSite ?place .
            ?place skos:prefLabel|skos:altLabel|skos:hiddenLabel ?label
        }""",
        'org-address': """
        SELECT ?thing ?label WHERE {
            ?thing rdf:type/rdfs:subClassOf* org:Organization ;
                v:adr/v:street-address ?label
        }""",
        'place-address': """
        SELECT ?thing ?label WHERE {
            ?thing org:hasSite/v:adr/v:street-address ?label
        }""",
    }

    parents_query = """
        SELECT ?child ?parent WHERE {
            ?child org:subOrganizationOf ?parent
        }"""

    def __init__(self):
        self.endpoint = Endpoint(settings.ENDPOINT_QUERY)
        self.dictionary = enchant.Dict("en_GB")

    @property
    def parents(self):
        if not hasattr(self, '_parents'):
            self._parents = self.get_parents()
        return self._parents

    @property
    def query_results(self):
        if not hasattr(self, '_query_results'):
            self._query_results = self.get_query_results()
        return self._query_results

    def get_parents(self):
        return dict((unicode(a), unicode(b)) for a, b in self.endpoint.query(self.parents_query))

    def get_query_results(self):
        query_results = {}
        for name in self.queries:
            query = self.queries[name]
            query_results[name] = collections.defaultdict(set)
            for result in self.endpoint.query(query):
                query_results[name][unicode(result.label)].add(unicode(result.thing))
            query_results[name] = dict(query_results[name])

        query_results['names'] = collections.defaultdict(set)
        for name, orgs in query_results['org-name'].iteritems():
            for org in orgs:
                query_results['names'][org].add(name)
        query_results['names'] = dict(query_results['names'])
        return query_results

    def guess(self, location, description, file_content):
        location = location.replace('Dept', 'Department') \
                           .replace('&', 'and')

        for guesses, uniquify in self.get_guess_queries(location):
            if guesses:
                break
        else:
            if 'Bodleian' in location:
                guesses, uniquify = set(['http://oxpoints.oucs.ox.ac.uk/id/23233598']), False
            else:
                return set(), set()

        guesses -= set(itertools.chain(*[self.get_ancestors(g)[1:] for g in guesses]))
        if len(guesses) > 1:
            guesses.discard('http://oxpoints.oucs.ox.ac.uk/id/54438284')

        roots = set()
        for guess in guesses:
            roots.add(self.get_ancestors(guess)[-1])

        if uniquify and len(guesses) > 1:
            #names = self.get_names
            pass

        return map(rdflib.URIRef, roots), map(rdflib.URIRef, guesses)

    def get_guess_queries(self, location):
        terms = set([' '.join(term.split()) for term in location.split(',')])
        for term in list(terms):
            if term.startswith('The '):
                terms.add(term[4:])
            if term.startswith('Department ') and not term.lower().startswith("department of"):
                terms.add("Department of " + term[11:])
            if term.startswith("Bodleian ") and term.lower().endswith(" library"):
                terms.add(term[9:])
                
        terms.discard("Oxford")

        results = lambda name, terms: \
            reduce(operator.or_, (self.query_results[name].get(term, set()) for term in terms))

        # Look for organisations by each of the names in the location
        yield results('org-name', terms), False

        # Try again, but correct any spelling mistakes
        yield results('org-name', map(self.correct_spelling, terms)), False

        match = re.search('and|And|&', location)
        if match:
            # Something like "Dept of Foo, Bar and Baz, University of Oxford"
            term = location[:location.find(',', match.start())]
            yield self.query_results['org-name'].get(term), False
            
            # Or a "Dept of Foo and Dept of Bar"
            new_terms = reduce(operator.or_, (set(t.strip() for t in re.split('and|And|&', term)) for term in terms))
            yield results('org-name', new_terms), False
            

        # What if they've used hyphens for delimiters?
        hyphenated_terms = [' '.join(term.split()) for term in location.split('-')]
        for term in hyphenated_terms:
            yield self.query_results['org-name'].get(term), False

        for query_name in ('place-name', 'org-address', 'place-address'):
            yield results(query_name, terms), True

    def correct_spelling(self, word):
        try:
            if self.dictionary.check(word):
                return word
            else:
                suggestions = self.dictionary.suggest(word)
                return suggestions[0] if suggestions else word
        except Exception:
            logger.exception("Spelling correction failed for %r", word)
            return word

    def get_ancestors(self, child):
        parents = []
        while child:
            parents.append(child)
            child = self.parents.get(child)
        return parents

    def get_names(self, org):
        return self.query_results['names'][unicode(org)]

    def _dump_query_results(self):
        # For testing purposes
        try:
            import json
        except ImportError:
            import simplejson as json
        json.dump(self.parents, open('parents.json', 'w'))
        query_results = dict((k, dict((k2, list(v2)) for k2, v2 in v.iteritems())) for k, v in self.query_results.iteritems())
        json.dump(query_results, open('query_results.json', 'w'))

