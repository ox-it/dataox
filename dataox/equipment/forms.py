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

class ContributeForm(forms.Form):
    manufacturer = forms.CharField()
    model = forms.CharField()
    description = forms.CharField(widget=forms.Textarea,
                                  help_text="What kind of things can it do? If there are any alterations, list them here.")
    quantity = forms.IntegerField()
    srf = forms.CharField(label="Name of Research Facility",
                          help_text="If this equipment is part of an SRF or MRF, provide its name here.",
                          required=False)
    availability = forms.CharField(widget=forms.Textarea,
                                   help_text="How much spare capacity does this equipment have?",
                                   required=False)
    access = forms.CharField(widget=forms.Textarea,
                             help_text="What groups of people are allowed to use it?",
                             required=False)
    useRestrictions = forms.CharField(widget=forms.Textarea,
                                      label="Restrictions on use:",
                                      help_text="e.g. funding body restrictions, training requirements, contamination issues",
                                      required=False)

    page = forms.URLField(required=False, label="Web page:")
    image = forms.URLField(label="Image URL:",
                           help_text="If there's a picture of this piece of equipment on the web, provide a link to it here.",
                           required=False)

    department = forms.CharField(widget=forms.TextInput(attrs={'class': 'autocomplete', 'data-type': 'organization'}))
    place = forms.CharField(widget=forms.TextInput(attrs={'class': 'autocomplete', 'data-type': 'spatial-thing'}),
                            label="Location",
                            help_text="Most likely a building, but maybe a room.")

    primary_contact_name = forms.CharField()
    primary_contact_email = forms.EmailField()

    secondary_contact_name = forms.CharField(required=False)
    secondary_contact_email = forms.EmailField(required=False)

    tertiary_contact_name = forms.CharField(required=False)
    tertiary_contact_email = forms.EmailField(required=False)

    university = forms.BooleanField(label="Show to members of the University?", required=False)
    seesec = forms.BooleanField(label="Show to members of other universities?", required=False)
    public = forms.BooleanField(label="Show to everyone?", required=False)

    notes = forms.CharField(widget=forms.Textarea, label="Anything else you'd like us to know?", required=False)
