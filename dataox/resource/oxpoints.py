from humfrey.linkeddata.resource import Resource
from humfrey.utils.namespaces import NS

class CollegeHall(object):
    @classmethod
    def _describe_patterns(cls):
        return [
#            '%(observation)s fhs:institution %(uri)s ; qb:dataset <http://data.ox.ac.uk/id/dataset/norrington>',
        ]

    def fhs_results(self):
        data = self._graph.subjects(NS['fhs'].institution, self._identifier)
        data = (Resource(datum, self._graph, self._endpoint) for datum in data)
        data = filter(lambda datum: datum.fhs_norringtonScore, data)
        data = sorted(data, key=lambda datum:datum.sdmxdim_timePeriod)
        for datum in data:
            datum.fhs_two_one = datum.get('fhs:two-one')
            datum.fhs_two_two = datum.get('fhs:two-two')
            datum.fhs_norringtonScore = '%.1f%%' % (datum.get('fhs:norringtonScore').toPython() * 100)
        return data

    def widget_templates(self):
        return [('widgets/norrington.html', self)] + super(CollegeHall, self).widget_templates()

class Organization(object):
    types = ('oxp:College', 'oxp:Hall', 'oxp:Faculty', 'oxp:Unit',
                            'oxp:Unit', 'oxp:Department', 'oxp:Library',
                            'oxp:University', 'org:Organization', 'oxp:Museum')
    def widget_templates(self):
        widgets = super(Organization, self).widget_templates()
        for account in self.all.foaf_account:
            widgets.extend(account.widget_templates())
        return widgets

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(uri)s foaf:account %(account)s',
        ]

class Place(object):
    types = ('oxp:Building', 'oxp:Site', 'oxp:Space', 'oxp:Room', 'org:Site',
             'rooms:Room', 'rooms:Building')

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(uri)s foaf:account %(account)s',
        ]
