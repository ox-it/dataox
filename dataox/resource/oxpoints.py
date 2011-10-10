from humfrey.utils.resource import Resource, register
from humfrey.utils.namespaces import NS

class CollegeHall(object):
    @classmethod
    def _describe_patterns(cls):
        return [
            '%(observation)s fhs:institution %(uri)s ; qb:dataset <http://data.ox.ac.uk/id/dataset/norrington>',
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
register(CollegeHall, 'oxp:Hall', 'oxp:College')

class Organization(object):
    def widget_templates(self):
        widgets = super(Organization, self).widget_templates()
        for account in self.all.foaf_account:
            widgets.extend(account.widget_templates())
        return widgets
register(Organization, 'oxp:College', 'oxp:Hall', 'oxp:Faculty', 'oxp:Unit', 'oxp:Department',
                       'oxp:Library', 'oxp:University', 'org:Organization')

class Place(object):
    @classmethod
    def _construct_patterns(cls):
        return [
            '%(meterPoint)s meter:pertainsTo %(uri)s ; timeseries:timeSeries ?timeSeries',
        ]

    @classmethod
    def _describe_patterns(cls):
        return [
            """%(uri)s ^meter:pertainsTo/timeseries:timeSeries %(timeSeries)s .
               OPTIONAL { %(timeSeries)s timeseries:sampling %(sampling)s } .
               OPTIONAL { %(timeSeries)s timeseries:include|timeseries:exclude %(subTimeSeries)s . %(subTimeSeries)s timeseries:sampling %(subSampling)s }""",
        ]
    
    def widget_templates(self):
        return [('widgets/openmeters.html', self),]
    
    def get_all_time_series(self):
        return [Resource(uri, self._graph, self._endpoint) for uri in self._graph.subjects(NS.rdf.type, NS.timeseries.TimeSeries)]
    def get_time_series(self):
        try:
            return self.meter_pertainsTo_inv.timeseries_timeSeries
        except AttributeError:
            return None
register(Place, 'oxp:Building', 'oxp:Site', 'oxp:Space', 'oxp:Room')
