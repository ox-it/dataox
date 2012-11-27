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

  <xsl:variable name="type">cerif:Facility</xsl:variable>
  <xsl:variable name="group-column">3</xsl:variable>
  <xsl:template name="uri">
    <xsl:text>https://data.ox.ac.uk/id/facility/</xsl:text>
    <xsl:value-of select="ex:slugify(tei:cell[3]/text())"/>
  </xsl:template>

  <xsl:template match="item/name-of-facility-service" mode="inside">
    <rdfs:label>
      <xsl:value-of select="text()"/>
    </rdfs:label>
    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/facility-rso">
      <xsl:value-of select="ex:slugify(text())"/>
    </skos:notation>
  </xsl:template>

  <xsl:template match="item/department-code" mode="inside">
    <oo:organizationPart>
      <org:Organization rdf:about="https://data.ox.ac.uk/id/equipment-department/{ex:slugify(text())}">
        <skos:notation>
          <xsl:attribute name="rdf:datatype">
            <xsl:text>https://data.ox.ac.uk/id/notation/</xsl:text>
            <xsl:choose>
              <xsl:when test="matches(., '^[A-Z\d]{2}$')">twoThree</xsl:when>
              <xsl:when test="matches(., '^\d{8}$')">oxpoints</xsl:when>
              <xsl:otherwise>department</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <xsl:value-of select="."/>
        </skos:notation>
        <rdfs:label>
          <xsl:value-of select="../department/normalize-space(text())"/>
        </rdfs:label>
      </org:Organization>
    </oo:organizationPart>
  </xsl:template>

  <xsl:template match="item/contact-email" mode="inside">
    <oo:contact>
      <foaf:Agent rdf:about="{../@uri}/contact">
        <xsl:if test="../contact-name/text()">
          <foaf:name>
            <xsl:value-of select="../contact-name/text()"/>
          </foaf:name>
        </xsl:if>
        <vcard:email rdf:resource="mailto:{text()}"/>
      </foaf:Agent>
    </oo:contact>
  </xsl:template>

  <!-- Columns we don't care about, which are handled in common.xsl -->
  <xsl:template match="item/availability" mode="inside"/>
  <xsl:template match="item/access" mode="inside"/>
  <xsl:template match="item/restrictions-on-use" mode="inside"/>

</xsl:stylesheet>
