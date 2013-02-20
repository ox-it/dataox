from django import forms
from humfrey.feeds.base import FeedForm, FeedView
from humfrey.utils.namespaces import contract

class OrganizationFeedForm(FeedForm):
    _types_query = """\
SELECT ?uri ?label WHERE {
  ?uri rdfs:subClassOf* org:Organization .
  OPTIONAL { ?uri rdfs:label ?label . FILTER(LANG(?label) = 'en-gb') }
  OPTIONAL { ?uri rdfs:label ?label . FILTER(LANG(?label) = 'en') }
  OPTIONAL { ?uri rdfs:label ?label }
  OPTIONAL { BIND(?uri AS ?label) }
}"""

    def __init__(self, *args, **kwargs):
        endpoint = kwargs['endpoint']
        types_choices = [(unicode(k), '{0} ({1})'.format(v, contract(k))) for k, v in endpoint.query(self._types_query)]
        types_choices.sort(key=lambda c: c[1])
        self.base_fields['type'].choices = types_choices
        super(OrganizationFeedForm, self).__init__(*args, **kwargs)

    type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                     help_text='The types of organisation to return. Selecting none will result in all types being returned.',
                                     required=False)
    oxpoints = forms.BooleanField(label="Just OxPoints",
                                  help_text="Only include organizations from OxPoints.",
                                  required=False)

class OrganizationFeedView(FeedView):
    name = 'organization'
    plural_name = 'organizations'
    description = 'Organizations, including units, colleges and PPHs from OxPoints'

    form_class = OrganizationFeedForm
    item_template = 'feeds-dataox/organization/item'
    query_template = 'feeds-dataox/organization/query.rq'

    orderings = {
        'sortLabel': ('Sort label', lambda s: s.ov_sortLabel or s.label),
        'oucsCode': ('Unit code', lambda s: s.oxp_hasOUCSCode),
        'financeCode': ('Two-three code', lambda s: s.oxp_hasFinanceCode),
        'departmentCode': ('Department code', lambda s: s.oxp_hasDepartmentCode),
    }
