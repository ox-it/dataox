<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oo="http://purl.org/openorg/"
    xmlns:cerif="http://spi-fm.uca.es/neologism/cerif#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:vcard="http://www.w3.org/2006/vcard/ns#"
    xmlns:spatialrelations="http://data.ordnancesurvey.co.uk/ontology/spatialrelations/"
    xmlns:srx="http://www.w3.org/2005/sparql-results#"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:ex="http://www.example.org/"
    xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:org="http://www.w3.org/ns/org#"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:tio="http://purl.org/tio/ns#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
  >
  <xsl:import href="common.xsl"/>

  <xsl:variable name="type">equipment</xsl:variable>
  <xsl:template name="uri">
    <xsl:text>https://data.ox.ac.uk/id/equipment/</xsl:text>
    <xsl:value-of select="tei:cell[2]/text()"/>
  </xsl:template>

  <xsl:output method="xml" indent="yes"/>
  <xsl:param name="store" select="'public'"/>
  <xsl:param name="output" select="'equipment'"/>

  <xsl:variable name="general-locations" select="document('')/xsl:stylesheet/ex:general-locations"/>
  <xsl:variable name="makes" select="document('')/xsl:stylesheet/ex:makes"/>
  <xsl:variable name="models" select="document('')/xsl:stylesheet/ex:makes"/>

  <xsl:key name="org-lookup" match="ex:org" use="@name"/>
  <xsl:key name="general-location-lookup" match="ex:general-location" use="@name"/>
  <xsl:key name="make-lookup" match="ex:make" use="@name"/>
  <xsl:key name="model-lookup" match="ex:model" use="@name"/>


  <xsl:template match="/">
    <xsl:variable name="equipment">
      <xsl:apply-templates select="//tei:table[1]/tei:row[position() &gt; 1]" mode="preprocess"/>
    </xsl:variable>
    <rdf:RDF>
      <xsl:choose>
        <xsl:when test="$output='equipment'">
          <xsl:apply-templates select="$equipment/equipment" mode="equipment"/>
        </xsl:when>
        <xsl:when test="$output='skos'">
          <xsl:apply-templates select="$equipment" mode="skos"/>
        </xsl:when>
      </xsl:choose>
    </rdf:RDF>
  </xsl:template>

    
  <xsl:template match="equipment" mode="equipment">
    <xsl:variable name="to-include">
      <xsl:choose>
        <xsl:when test="$store='public'"><xsl:value-of select="public"/></xsl:when>
        <xsl:when test="$store='equipment'"><xsl:value-of select="university"/></xsl:when>
        <xsl:when test="$store='seesec'"><xsl:value-of select="seesec"/></xsl:when>
        <xsl:otherwise>
          <xsl:message terminate="yes">Unexpected store: <xsl:value-of select="store"/></xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:if test="$to-include='Yes' or $store='public'">
      <cerif:Equipment rdf:about="{@uri}">
        <!-- Everything is part of the University of Oxford -->
        <oo:formalOrganization rdf:resource="http://oxpoints.oucs.ox.ac.uk/id/00000000"/>

        <xsl:if test="$to-include='Yes'">
          <xsl:apply-templates select="*" mode="inside"/>
          <xsl:choose>
            <xsl:when test="quantity/text() &gt; 1">
              <rdf:type rdf:resource="http://purl.org/goodrelations/v1#SomeItems"/>
              <gr:hasInventoryLevel>
                <gr:QuantitativeValue rdf:about="{@uri}/quantity">
                  <gr:hasValue rdf:datatype="http://www.w3.org/2001/XMLSchema#int">
                    <xsl:value-of select="quantity/text()"/>
                  </gr:hasValue>
                </gr:QuantitativeValue>
              </gr:hasInventoryLevel>
            </xsl:when>
            <xsl:otherwise>
              <rdf:type rdf:resource="http://purl.org/goodrelations/v1#Individual"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
      </cerif:Equipment>
      <xsl:if test="$to-include='Yes'">
        <xsl:apply-templates select="*" mode="outside"/>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <xsl:template match="unique-identifier" mode="inside">
    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/equipment-rso">
      <xsl:value-of select="text()"/>
    </skos:notation>
  </xsl:template>

  <xsl:template match="model" mode="inside">
    <rdfs:label>
      <xsl:value-of select="normalize-space(concat(../make, ' ', .))"/>
    </rdfs:label>

    <xsl:variable name="make-details" select="key('make-lookup', ../make/text(), $makes)"/>
    <xsl:variable name="model-details" select="key('model-lookup', text(), $models)"/>
    <xsl:variable name="make-uri">
      <xsl:choose>
        <xsl:when test="$make-details">
          <xsl:value-of select="$make-details/@uri"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat('https://data.ox.ac.uk/id/equipment-model/', ex:slugify(../make/text()))"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="model-uri">
      <xsl:choose>
        <xsl:when test="$make-details and $model-details">
          <xsl:value-of select="concat('https://data.ox.ac.uk/id/equipment-model/', $make-details/@short, '/', $model-details/@short)"/>
        </xsl:when>
        <xsl:when test="$make-details">
          <xsl:value-of select="concat('https://data.ox.ac.uk/id/equipment-model/', $make-details/@short, '/', ex:slugify(text()))"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat($make-uri, '/', ex:slugify(text()))"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <gr:hasMakeAndModel>
      <gr:ProductOrServiceModel rdf:about="{$model-uri}">
        <gr:name>
          <xsl:value-of select="."/>
        </gr:name>
        <gr:hasManufacturer>
          <gr:BusinessEntity rdf:about="{$make-uri}">
            <gr:name>
              <xsl:value-of select="../make"/>
            </gr:name>
            <xsl:apply-templates select="$make-details" mode="pages"/>
          </gr:BusinessEntity>
        </gr:hasManufacturer>
        <xsl:apply-templates select="$model-details" mode="pages"/>
      </gr:ProductOrServiceModel>
    </gr:hasMakeAndModel>
  </xsl:template>

  <xsl:template match="equipment-details" mode="inside">
    <rdfs:comment>
      <xsl:value-of select="normalize-space(.)"/>
    </rdfs:comment>
  </xsl:template>

  <xsl:template match="general-location" mode="inside">
    <xsl:variable name="general-location" select="key('general-location-lookup', text(), $general-locations)"/>
    <xsl:if test="text()">
      <foaf:based_near>
        <xsl:choose>
          <xsl:when test="$general-location/@oxpoints">
            <geo:SpatialThing rdf:about="https://data.ox.ac.uk/equipment-location/{ex:slugify(text())}">
              <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/oxpoints">
                <xsl:value-of select="$general-location/@oxpoints"/>
              </skos:notation>
            </geo:SpatialThing>
          </xsl:when>
          <xsl:when test="$general-location/@uri">
            <geo:SpatialThing rdf:about="{$general-location/@uri}">
              <rdfs:label>
                <xsl:value-of select="$general-location/@label"/>
              </rdfs:label>
            </geo:SpatialThing>
          </xsl:when>
          <xsl:otherwise>
            <geo:SpatialThing rdf:about="https://data.ox.ac.uk/id/equipment-general-location/{ex:slugify(text())}">
              <rdfs:label>
                <xsl:value-of select="normalize-space(text())"/>
              </rdfs:label>
            </geo:SpatialThing>
          </xsl:otherwise>
        </xsl:choose>
      </foaf:based_near>
    </xsl:if>
  </xsl:template>

  <xsl:template match="primary-contact-email|secondary-contact-email|tertiary-contact-email" mode="inside">
    <xsl:variable name="contact-name">
      <xsl:choose>
        <xsl:when test="self::primary-contact-email"><xsl:value-of select="../primary-contact-name"/></xsl:when>
        <xsl:when test="self::secondary-contact-email"><xsl:value-of select="../secondary-contact-name"/></xsl:when>
        <xsl:when test="self::tertiary-contact-email"><xsl:value-of select="../tertiary-contact-name"/></xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="uri-part">
      <xsl:choose>
        <xsl:when test="self::primary-contact-email">primary-contact</xsl:when>
        <xsl:when test="self::secondary-contact-email">secondary-contact</xsl:when>
        <xsl:when test="self::tertiary-contact-email">tertiary-contact</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$store != 'public'">
      <oo:contact>
        <foaf:Agent rdf:about="{../@uri}/{$uri-part}">
          <xsl:if test="$contact-name">
            <foaf:name><xsl:value-of select="$contact-name"/></foaf:name>
          </xsl:if>
          <vcard:email rdf:resource="mailto:{text()}"/>
        </foaf:Agent>
      </oo:contact>
      <xsl:if test="$uri-part = 'primary-contact'">
        <oo:primaryContact rdf:resource="{../@uri}/{$uri-part}"/>
      </xsl:if>
    </xsl:if>
  </xsl:template>


  <!-- SKOS Concept Scheme generation -->
  <xsl:template match="/" mode="skos">
    <skos:ConceptScheme rdf:about="https://data.ox.ac.uk/id/equipment-category">
      <skos:prefLabel>Taxonomy for research facilities and equipment at the University of Oxford</skos:prefLabel>
      <dcterms:publisher rdf:resource="http://oxpoints.oucs.ox.ac.uk/id/23233536"/>
      <xsl:for-each-group select="equipment" group-by="ex:slugify(category)">
        <skos:hasTopConcept>
          <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-category/{ex:slugify(category)}">
            <skos:prefLabel>
              <xsl:value-of select="category"/>
            </skos:prefLabel>
            <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/equipment-category">
              <xsl:value-of select="ex:slugify(category)"/>
            </skos:notation>
            <xsl:for-each-group select="current-group()" group-by="ex:slugify(subcategory)">
              <skos:narrower>
                <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-category/{ex:slugify(category)}/{ex:slugify(subcategory)}">
                  <skos:prefLabel>
                    <xsl:value-of select="subcategory"/>
                  </skos:prefLabel>
                  <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/equipment-category">
                    <xsl:value-of select="concat(ex:slugify(category), '/', ex:slugify(subcategory))"/>
                  </skos:notation>
                </skos:Concept>
              </skos:narrower>
            </xsl:for-each-group>

          </skos:Concept>
        </skos:hasTopConcept>
      </xsl:for-each-group>

    </skos:ConceptScheme>
    <skos:ConceptScheme rdf:about="https://data.ox.ac.uk/id/equipment-shareability">
      <skos:prefLabel>Taxonomy of equipment shareability statuses</skos:prefLabel>
      <dcterms:publisher rdf:resource="http://oxpoints.oucs.ox.ac.uk/id/23233536"/>
      <skos:hasTopConcept>
        <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-shareability/yes">
          <skos:prefLabel>yes</skos:prefLabel>
          <skos:definition>The item will likely be available for use by members of the University of Oxford.</skos:definition>
        </skos:Concept>
      </skos:hasTopConcept>
      <skos:hasTopConcept>
        <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-shareability/contact">
          <skos:prefLabel>contact for details</skos:prefLabel>
          <skos:definition>No information is held about whether the item is able to be shared. Please contact for more information.</skos:definition>
        </skos:Concept>
      </skos:hasTopConcept>
      <skos:hasTopConcept>
        <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-shareability/no">
          <skos:prefLabel>contact for details</skos:prefLabel>
          <skos:definition>It is unlikely that the item is available for re-use by others.</skos:definition>
        </skos:Concept>
      </skos:hasTopConcept>
    </skos:ConceptScheme>
        
  </xsl:template>
<!--
        <skos:hasTopConcept>
          <skos:Concept rdf:about="http://data.ox.ac.uk/id/equipment-category/{ex:slugify($category)}">
            <skos:prefLabel>
              <xsl:value-of select="$category"/>
            </skos:prefLabel>
            <skos:notation rdf:datatype="http://data.ox.ac.uk/id/notation/equipment-category">
              <xsl:value-of select="ex:slugify($category)"/>
            </skos:notation>
            <skos:narrower>
              <skos:Concept rdf:about="http://data.ox.ac.uk/id/equipment-category/{ex:slugify($category)}/{ex:slugify($subcategory)}">
                <skos:prefLabel>
                  <xsl:value-of select="$subcategory"/>
                </skos:prefLabel>
                <skos:notation rdf:datatype="http://data.ox.ac.uk/id/notation/equipment-category">
                  <xsl:value-of select="concat(ex:slugify($category), '/', ex:slugify($subcategory))"/>
                </skos:notation>
              </skos:Concept>
            </skos:narrower>
          </skos:Concept>
        </skos:hasTopConcept>
      </skos:ConceptScheme>
    </xsl:if>
  </xsl:template>
-->

  <xsl:template match="*" mode="pages">
    <xsl:if test="@page">
      <foaf:page rdf:resource="{@page}"/>
    </xsl:if>
    <xsl:if test="@homepage">
      <foaf:homepage rdf:resource="{@homepage}"/>
    </xsl:if>
  </xsl:template>

  <ex:general-locations>
    <ex:general-location name="Headington" uri="http://dbpedia.org/resource/Headington" label="Headington"/>
    <ex:general-location name="Science Area" oxpoints="59030245"/>
    <ex:general-location name="Oxford Science Area" oxpoints="59030245"/>
    <ex:general-location name="Begbroke Science Park" oxpoints="51219523"/>
    <!-- We don't have a URI for this yet
    <ex:general-location name="Osney Mead Industrial Estate"/>
    -->
    <ex:general-location name="Wytham" uri="http://dbpedia.org/resource/Wytham" label="Wytham"/>
    <ex:general-location name="HCMC" uri="http://dbpedia.org/resource/Ho_Chi_Minh_City" label="Ho Chi Minh City"/>
    <ex:general-location name="New York" uri="http://dbpedia.org/resource/New_York" label="New York"/>
    <ex:general-location name="Toronto" uri="http://dbpedia.org/resource/Toronto" label="Toronto"/>
    <ex:general-location name="Maesot" uri="http://dbpedia.org/resource/Mae_Sot_District" label="Mae Sot"/>
    <ex:general-location name="Zimbabwe" uri="http://dbpedia.org/resource/Zimbabwe" label="Zimbabwe"/>
  </ex:general-locations>

  <ex:makes>
    <ex:make name="2G Enterprises" uri="http://opencorporates.com/id/companies/us_fl/L11000084534" short="2g-enterprises">
      <ex:model name="755-1.65 UC" short="755-1.65-uc" page="http://wsgi.us/catalog.html#SRM"/>
    </ex:make>
    <ex:make name="3DHISTECH" uri="http://opencorporates.com/id/companies/us_dc/295747" short="3dhistech"/>
    <ex:make name="3dMD" uri="http://opencorporates.com/id/companies/gb/04080651" short="3dmd"/>
  </ex:makes>

</xsl:stylesheet>

