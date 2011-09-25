import itertools
import re

import enchant
import rdflib


from django.conf import settings
from humfrey.utils.namespaces import NS
from humfrey.utils.sparql import Endpoint

class LocationGuesser(object):

    queries = {
        'org-name': """
        SELECT ?thing WHERE {
            ?thing skos:prefLabel|skos:altLabel|skos:hiddenLabel %s ; rdf:type/rdfs:subClassOf* org:Organization
        }""",
        'place-name': """
        SELECT ?thing WHERE {
            ?thing org:hasSite ?place .
            ?place skos:prefLabel|skos:altLabel|skos:hiddenLabel %s
        }""",
        'org-address': """
        SELECT ?thing WHERE {
            ?thing v:adr/v:street-address %s ; rdf:type/rdfs:subClassOf* org:Organization
        }""",
        'place-address': """
        SELECT ?thing WHERE {
            ?thing org:hasSite/v:adr/v:street-address %s
        }""",
        'parents': """
        SELECT ?child ?parent WHERE {
            ?child org:subOrganizationOf ?parent
        }""",
    }

    def __init__(self):
        self.endpoint = Endpoint(settings.ENDPOINT_QUERY)
        self.dictionary = enchant.Dict("en_GB")

        self.parents = dict((a._identifier, b._identifier) for a, b in self.endpoint.query(self.queries['parents']))

    def guess(self, location, description, file_content):
        location = location.replace('Dept', 'Department') \
                           .replace('&', 'and')

        for query, uniquify in self.get_guess_queries(location):
            guesses = self.get_guesses(query)
            if guesses:
                break
        else:
            return set(), set()

        guesses -= set(itertools.chain(*[self.get_parents(g)[1:] for g in guesses]))

        roots = set()
        for guess in guesses:
            roots.add(self.get_parents(guess)[-1])

        if uniquify and len(guesses) > 1:
            #names = self.get_names
            pass

        return roots, guesses

    def get_guess_queries(self, location):
        terms = [' '.join(term.split()) for term in location.split(',')]

        query = lambda query_name, term: self.queries[query_name] % rdflib.Literal(term, datatype=NS.xsd.string).n3()

        # Look for organisations by each of the names in the location
        for term in terms:
            yield query('org-name', term), False

        # Try again, but correct any spelling mistakes
        for term in terms:
            new_term = ' '.join(map(self.correct_spelling, term.split()))
            if new_term != term:
                yield query('org-name', new_term), False

        # Something like "Dept of Foo, Bar and Baz, University of Oxford"
        match = re.search('and|And|&', location)
        if match:
            term = location[:location.find(',', match.start())]
            yield query('org-name', term), False

        # What if they've used hyphens for delimiters?
        hyphenated_terms = [' '.join(term.split()) for term in location.split('-')]
        for term in hyphenated_terms:
            yield query('org-name', term), False

        for term in terms:
            for query_name in ('place-name', 'org-address', 'place-address'):
                yield query(query_name, term), True


    def get_guesses(self, query):
        results = self.endpoint.query(query)
        return set([r.thing._identifier for r in results])

    def correct_spelling(self, word):
        if self.dictionary.check(word):
            return word
        else:
            suggestions = self.dictionary.suggest(word)
            return suggestions[0] if suggestions else word

    def get_parents(self, child):
        parents = []
        while child:
            parents.append(child)
            child = self.parents.get(child)
        return parents
