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
    xmlns:void="http://rdfs.org/ns/void#"
    xmlns:cat="http://purl.org/NET/catalog/"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
  >
  <xsl:import href="common.xsl"/>

  <xsl:variable name="type">cerif:Equipment</xsl:variable>
  <xsl:variable name="catalog-uri">https://data.ox.ac.uk/id/dataset/research-facilities/equipment</xsl:variable>
  <xsl:template name="record-uri">
    <xsl:text>https://data.ox.ac.uk/id/equipment-record/</xsl:text>
    <xsl:value-of select="tei:cell[2]/text()"/>
  </xsl:template>
  <xsl:template name="uri">
    <xsl:text>https://data.ox.ac.uk/id/equipment/</xsl:text>
    <xsl:value-of select="tei:cell[2]/text()"/>
  </xsl:template>


  <xsl:variable name="general-locations" select="document('')/xsl:stylesheet/ex:general-locations"/>
  <xsl:variable name="makes" select="document('')/xsl:stylesheet/ex:makes"/>
  <xsl:variable name="models" select="document('')/xsl:stylesheet/ex:makes"/>
  <xsl:variable name="document" select="/"/>

  <xsl:key name="org-lookup" match="ex:org" use="@name"/>
  <xsl:key name="general-location-lookup" match="ex:general-location" use="@name"/>
  <xsl:key name="make-lookup" match="ex:make" use="@name"/>
  <xsl:key name="model-lookup" match="ex:model" use="@name"/>

  <xsl:template match="/" mode="in-catalog">
    <xsl:variable name="items" select="/"/>
    <xsl:apply-imports/>
    <xsl:for-each select="$document//tei:table[tei:head='Updates']/tei:row[position() gt 1]">
      <xsl:variable name="department-code" select="tei:cell[1]/text()"/>
      <void:subset>
        <cat:Catalog rdf:about="https://data.ox.ac.uk/id/dataset/research-facilities/equipment/{ex:slugify(tei:cell[1])}">
	  <rdf:type rdf:resource="http://rdfs.org/ns/void#Dataset"/>
	  <rdfs:label>
	    <xsl:text>Equipment from </xsl:text>
	    <xsl:value-of select="tei:cell[2]"/>
	  </rdfs:label>
	  <oo:organizationPart>
	    <rdf:Description>
	      <xsl:apply-templates select="$department-code" mode="department-code-notation"/>
	    </rdf:Description>
	  </oo:organizationPart>
	  <dcterms:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#gYearMonth">
	    <xsl:value-of select="tei:cell[3]"/>
          </dcterms:issued>
	  <xsl:apply-templates select="$items/item[department-code/text()=$department-code]" mode="catalog-record-links"/>
	</cat:Catalog>
      </void:subset>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="item/quantity" mode="inside">
    <xsl:choose>
      <xsl:when test="number(text()) != number(text())">
        <rdf:type rdf:resource="http://purl.org/goodrelations/v1#SomeItems"/>
      </xsl:when>
      <xsl:when test="text() &gt; 1">
        <rdf:type rdf:resource="http://purl.org/goodrelations/v1#SomeItems"/>
        <gr:hasInventoryLevel>
          <gr:QuantitativeValueFloat rdf:about="{../@uri}/quantity">
            <gr:hasValueFloat rdf:datatype="http://www.w3.org/2001/XMLSchema#int">
              <xsl:value-of select="text()"/>
            </gr:hasValueFloat>
          </gr:QuantitativeValueFloat>
        </gr:hasInventoryLevel>
      </xsl:when>
      <xsl:otherwise>
        <rdf:type rdf:resource="http://purl.org/goodrelations/v1#Individual"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="item/unique-identifier" mode="inside">
    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/equipment-rso">
      <xsl:value-of select="text()"/>
    </skos:notation>
  </xsl:template>

  <xsl:template match="item/model" mode="inside">
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
        <xsl:when test="../make/text()">
          <xsl:value-of select="concat('https://data.ox.ac.uk/id/equipment-model/', ex:slugify(../make/text()))"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>https://data.ox.ac.uk/id/equipment-model/-</xsl:text>
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
        <xsl:if test="../make/text()">
          <gr:hasManufacturer>
            <gr:BusinessEntity rdf:about="{$make-uri}">
              <gr:name>
                <xsl:value-of select="../make"/>
              </gr:name>
              <xsl:apply-templates select="$make-details" mode="pages"/>
            </gr:BusinessEntity>
          </gr:hasManufacturer>
        </xsl:if>
        <xsl:apply-templates select="$model-details" mode="pages"/>
      </gr:ProductOrServiceModel>
    </gr:hasMakeAndModel>
  </xsl:template>

  <xsl:template match="item/equipment-details" mode="inside">
    <xsl:apply-templates select="." mode="xhtml-or-text">
      <xsl:with-param name="name">rdfs:comment</xsl:with-param>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="item/general-location" mode="inside">
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

  <xsl:template match="item/small-research-facility" mode="inside">
    <xsl:if test="text() and lower-case(text())!='no'">
      <oo:relatedFacility>
        <cerif:Facility rdf:about="{../@uri}/facility">
          <rdfs:label>
            <xsl:value-of select="text()"/>
          </rdfs:label>
          <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/facility-rso">
            <xsl:value-of select="ex:slugify(text())"/>
          </skos:notation>
        </cerif:Facility>
      </oo:relatedFacility>
    </xsl:if>
  </xsl:template>

  <xsl:template match="item/keywords" mode="inside">
    <xsl:for-each select="tokenize(text(), ';')">
      <dc:subject>
        <xsl:value-of select="normalize-space(.)"/>
      </dc:subject>
    </xsl:for-each>
  </xsl:template>

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
    <ex:general-location name="London" uri="http://dbpedia.org/resource/London" label="London"/>
    <ex:general-location name="Vientiane" uri="http://dbpedia.org/resource/Vientiane" label="Vientiane"/>
    <ex:general-location name="Harwell" uri="http://dbpedia.org/resource/Harwell,_Oxfordshire" label="Harwell"/>
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

