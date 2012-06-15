from humfrey.linkeddata.resource import ResourceRegistry

import dataox.resource

class Equipment(object):
    template_name = 'equipment/view/equipment'

    types = ('oo:Equipment', 'cerif:Equipment')

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(uri)s oo:contact %(contact)s . OPTIONAL { %(contact)s v:tel %(telephone)s }',
            '%(uri)s oo:accessPrerequisite %(accessPrerequisite)s',
            '%(uri)s oo:useRestriction %(useRestriction)s',
            '%(uri)s oo:availability %(availability)s',
            '%(uri)s dcterms:subject %(category)s',
            
            '%(uri)s oo:organizationPart %(department)s',
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
        return self.get_all('oo:organizationPart', inverse=True)

class Place(dataox.resource.oxpoints.Place):
    template_name = 'equipment/view/place'

    @classmethod
    def _describe_patterns(cls):
        return [
            '%(equipment)s spatialrelations:within+ %(uri)s',
        ]

    @classmethod
    def _construct_patterns(cls):
        return [
            # Add direct spatialrelations:within property where there is a chain.
            ('%(equipment)s spatialrelations:within %(uri)s', '%(equipment)s spatialrelations:within+ %(uri)s'),
        ]

resource_registry = dataox.resource.resource_registry + ResourceRegistry(
    Equipment, Organization, Place
)

