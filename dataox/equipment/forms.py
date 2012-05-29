import json
import urllib2

from django import forms
import rdflib

from humfrey.sparql.utils import get_labels

def AdvancedSearchForm(*args, **kwargs):
    search_url, store = kwargs.pop('search_url'), kwargs.pop('store')

    q = {'size': 0,
         'facets': {'formalOrganisation': {'terms': {'field': 'formalOrganisation.uri'}},
                    'basedNear': {'terms': {'field': 'basedNear.uri'}}}}
    
    results = json.load(urllib2.urlopen(search_url, json.dumps(q)))
    
    formal_organisation_choices = [t['term'] for t in results['facets']['formalOrganisation']['terms']]
    based_near_choices = [t['term'] for t in results['facets']['basedNear']['terms']]
    
    labels = get_labels(formal_organisation_choices + based_near_choices,
                        endpoint=store.query_endpoint)
    
    formal_organisation_choices = [('', '-'*20)]+[(uri, labels[rdflib.URIRef(uri)]) for uri in formal_organisation_choices]
    based_near_choices = [('', '-'*20)]+[(uri, labels[rdflib.URIRef(uri)]) for uri in based_near_choices]

    attrs = {'q': forms.CharField(label='Query'),
             'filter.basedNear.uri': forms.ChoiceField(label='Location',
                                                       choices=based_near_choices,
                                                       initial=''),
             'filter.formalOrganisation.uri': forms.ChoiceField(label='Institution',
                                                                choices=formal_organisation_choices,
                                                                initial='http://oxpoints.oucs.ox.ac.uk/id/00000000')}
    form = type('AdvancedSearchForm', (forms.Form,), attrs)
    
    return form(*args, **kwargs)
