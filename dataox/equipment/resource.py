from humfrey.linkeddata.resource import ResourceRegistry
from humfrey.utils.namespaces import NS, expand

import dataox.resource

equipment_types = set(map(expand, ['oo:Equipment', 'cerif:Equipment']))
facility_types = set(map(expand, ['oo:Facility', 'cerif:Facility']))

class Equipment(object):
    template_name = 'equipment/view/equipment'
    search_item_template_name = 'search_item/equipment'

    types = tuple(equipment_types)

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(uri)s oo:contact %(contact)s . OPTIONAL { %(contact)s v:tel %(telephone)s }',
            '%(uri)s oo:accessPrerequisite %(accessPrerequisite)s',
            '%(uri)s oo:useRestriction %(useRestriction)s',
            '%(uri)s oo:availability %(availability)s',
            '%(uri)s dcterms:subject %(category)s',
            
            '%(uri)s oo:organizationPart %(department)s',
            '%(uri)s oo:formalOrganization %(department)s',
            '%(uri)s oo:relatedFacility %(department)s',
            '%(uri)s foaf:based_near %(basedNear)s',
            '%(uri)s spatialrelations:within %(within)s',
            '%(uri)s gr:hasMakeAndModel %(makeAndModel)s . %(makeAndModel)s gr:hasManufacturer %(manufacturer)s',
            '%(uri)s gr:hasInventoryLevel %(inventoryLevel)s',
        ]
        
    @property
    def geo_provider(self):
        return self.spatialrelations_within or self.foaf_based_near
    
    @property
    def geo_lat(self):
        return self.geo_provider.geo_lat if self.geo_provider else None

    @property
    def geo_long(self):
        return self.geo_provider.geo_long if self.geo_provider else None

class Facility(object):
    template_name = 'equipment/view/facility'

    types = tuple(facility_types)

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(equipment)s oo:relatedFacility %(uri)s',
            '%(uri)s dcterms:subject %(category)s',
            '%(uri)s oo:organizationPart %(department)s',
            '%(uri)s oo:formalOrganization %(department)s',
            '%(uri)s oo:contact %(contact)s . OPTIONAL { %(contact)s v:tel %(telephone)s }',
        ]

class Organization(dataox.resource.oxpoints.Organization):
    template_name = 'equipment/view/organization'

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(equipment)s oo:organizationPart %(uri)s',
            #'%(equipment)s oo:organizationPart %(uri)s',
            #'%(equipment)s oo:accessPrerequisite %(accessPrerequisite)s',
            #'%(equipment)s oo:useRestriction %(useRestriction)s',
            #'%(equipment)s oo:availability %(availability)s',
            #'%(equipment)s dcterms:subject %(category)s',
        ]

    @classmethod
    def _construct_patterns(cls):
        return [
            """%(equipment)s oo:organizationPart %(uri)s ;
                   oo:availability %(equipmentAvailability)s .
               %(equipmentAvailability)s a %(equipmentAvailabilityType)s ;
                   rdfs:label %(equipmentAvailabilityLabel)s""",
        ]

    @property
    def allEquipment(self):
        return [r for r in self.get_all('oo:organizationPart', inverse=True) if set(t._identifier for t in r.get_all('rdf:type')) & equipment_types]

    @property
    def allFacilities(self):
        return [r for r in self.get_all('oo:organizationPart', inverse=True) if set(t._identifier for t in r.get_all('rdf:type')) & facility_types]

class Place(dataox.resource.oxpoints.Place):
    template_name = 'equipment/view/place'

    @classmethod
    def _describe_patterns(cls):
        return [
            """%(equipment)s spatialrelations:within+ %(uri)s ; a ?equipmentType .
               NOT EXISTS {
                 %(equipment)s spatialrelations:within+ ?building . ?building spatialrelations:within+ %(uri)s .
                 ?building rdf:type/rdfs:subClassOf* ?building
               }
               EXISTS {
                 { ?equipmentType rdfs:subClassOf* oo:Equipment }
                 UNION
                 { ?equipmentType rdfs:subClassOf* cerif:Equipment }
               }""",
        ]

    @classmethod
    def _construct_patterns(cls):
        return [
            # Add direct spatialrelations:within property where there is a chain.
            ('%(equipment)s spatialrelations:within %(uri)s',
             """%(equipment)s spatialrelations:within+ %(uri)s .
                NOT EXISTS {
                  %(equipment)s spatialrelations:within+ ?building . ?building spatialrelations:within+ %(uri)s .
                  ?building rdf:type/rdfs:subClassOf* ?building
                }"""),
            ('%(child)s spatialrelations:within %(parent)s. %(parent)s a %(parentType)s',
             '%(uri)s spatialrelations:within* %(child)s . %(child)s spatialrelations:within %(parent)s. %(parent)s a %(parentType)s'),
        ]

    @property
    def hierarchy(self):
        ancestors, ancestor = [], self
        while ancestor:
            ancestors.insert(0, ancestor)
            ancestor = ancestor.get('spatialrelations:within')
        return ancestors

    @property
    def allEquipment(self):
        contained = self.get_all('spatialrelations:within', inverse=True)
        return [item for item in contained if set(self._graph.objects(item._identifier, NS.rdf.type)) & equipment_types]

resource_registry = dataox.resource.resource_registry + ResourceRegistry(
    Equipment, Facility, Organization, Place
)

