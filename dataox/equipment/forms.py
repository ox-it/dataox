import json
import urllib.request

from django import forms
import rdflib

from humfrey.sparql.utils import get_labels

def AdvancedSearchForm(*args, **kwargs):
    search_url, store = kwargs.pop('search_url'), kwargs.pop('store')

    q = {'size': 0,
         'facets': {'formalOrganisation': {'terms': {'field': 'formalOrganisation.uri'}},
                    'basedNear': {'terms': {'field': 'basedNear.uri'}}}}

    results = json.load(urllib.request.urlopen(search_url, json.dumps(q)))

    formal_organisation_choices = [t['term'] for t in results['facets']['formalOrganisation']['terms']]
    based_near_choices = [t['term'] for t in results['facets']['basedNear']['terms']]

    labels = get_labels(map(rdflib.URIRef, formal_organisation_choices + based_near_choices),
                        endpoint=store.query_endpoint)

    formal_organisation_choices = [('', '-'*20)]+[(uri, labels.get(rdflib.URIRef(uri), uri)) for uri in formal_organisation_choices]
    based_near_choices = [('', '-'*20)]+[(uri, labels.get(rdflib.URIRef(uri), uri)) for uri in based_near_choices]

    attrs = {'q': forms.CharField(label='Query'),
             'filter.basedNear.uri': forms.ChoiceField(label='Location',
                                                       choices=based_near_choices,
                                                       initial='',
                                                       required=False),
             'filter.formalOrganisation.uri': forms.ChoiceField(label='Institution',
                                                                choices=formal_organisation_choices,
                                                                initial='http://oxpoints.oucs.ox.ac.uk/id/00000000',
                                                                required=False)}
    form = type('AdvancedSearchForm', (forms.Form,), attrs)

    return form(*args, **kwargs)

class ContributeForm(forms.Form):
    manufacturer = forms.CharField(label="Manufacturer:")
    model = forms.CharField(label="Model:")
    description = forms.CharField(widget=forms.Textarea,
                                  label="Description:",
                                  help_text="What kind of things can it do? If there are any alterations, list them here.")
    category = forms.CharField(widget=forms.TextInput(attrs={'class': 'dataox-autocomplete',
                                                             'data-autocomplete-type': 'equipment-category'}),
                               label="Category:",
                               required=False)
    quantity = forms.IntegerField(label="Quantity:")
    srf = forms.CharField(label="Name of Research Facility:",
                          help_text="If this equipment is part of an SRF or MRF, provide its name here.",
                          required=False)
    availability = forms.CharField(widget=forms.Textarea,
                                   label="Availability:",
                                   help_text="How much spare capacity does this equipment have?",
                                   required=False)
    access = forms.CharField(widget=forms.Textarea,
                             label="Access:",
                             help_text="What groups of people are allowed to use it?",
                             required=False)
    useRestrictions = forms.CharField(widget=forms.Textarea,
                                      label="Restrictions on use:",
                                      help_text="e.g. funding body restrictions, training requirements, contamination issues",
                                      required=False)

    page = forms.URLField(label="Web page:",
                          required=False)
    image = forms.URLField(label="Image URL:",
                           help_text="If there's a picture of this piece of equipment on the web, provide a link to it here.",
                           required=False)

    department = forms.CharField(widget=forms.TextInput(attrs={'class': 'dataox-autocomplete',
                                                               'data-autocomplete-type': 'organization',
                                                               'data-autocomplete-filter.graph.uri': 'https://data.ox.ac.uk/graph/oxpoints/data'}),
                                 label="Department:")
    place = forms.CharField(widget=forms.TextInput(attrs={'class': 'dataox-autocomplete',
                                                          'data-autocomplete-type': 'spatial-thing',
                                                          'data-autocomplete-filter.graph.uri': 'https://data.ox.ac.uk/graph/oxpoints/data'}),
                            label="Location",
                            help_text="Most likely a building, but maybe a room.")

    primary_contact_name = forms.CharField(label="Primary contact name:")
    primary_contact_email = forms.EmailField(label="Primary contact email:")

    secondary_contact_name = forms.CharField(label="Secondary contact name:",
                                             required=False)
    secondary_contact_email = forms.EmailField(label="Secondary contact email:",
                                               required=False)

    tertiary_contact_name = forms.CharField(label="Tertiary contact name:",
                                            required=False)
    tertiary_contact_email = forms.EmailField(label="Tertiary contact email:",
                                              required=False)

    university = forms.BooleanField(label="Show to members of the University?",
                                    required=False)
    seesec = forms.BooleanField(label="Show to members of other universities?",
                                required=False)
    public = forms.BooleanField(label="Show to everyone?",
                                required=False)

    notes = forms.CharField(widget=forms.Textarea,
                            label="Anything else you'd like us to know?",
                            required=False)
