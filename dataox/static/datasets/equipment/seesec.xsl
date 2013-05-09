<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:aiiso="http://purl.org/vocab/aiiso/schema#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xmlns:spatialrelations="http://data.ordnancesurvey.co.uk/ontology/spatialrelations/"
    xmlns:rooms="http://vocab.deri.ie/rooms#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:oo="http://purl.org/openorg/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:tio="http://purl.org/tio/ns#"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    xmlns:ex="http://www.example.org/"
    xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
    xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns="https://github.com/ox-it/python-sharepoint/"
    xpath-default-namespace="https://github.com/ox-it/python-sharepoint/"
    version="2.0">
  <xsl:import href="../common/slugify.xsl"/>
  <xsl:output method="xml" indent="yes"/>

  <xsl:param name="provider-slug"/>
  <xsl:param name="provider-uri">
    <xsl:value-of select="concat('https://data.ox.ac.uk/id/ses-external/', $provider-slug)"/>
  </xsl:param>
  <xsl:param name="provider-name"/>
  <xsl:variable name="base-uri" select="concat('https://data.ox.ac.uk/id/ses-external/', $provider-slug, '/')"/>

  <xsl:template match="/">
    <rdf:RDF>
      <aiiso:Insitution rdf:about="{$provider-uri}">
        <rdfs:label>
          <xsl:value-of select="$provider-name"/>
        </rdfs:label>
      </aiiso:Insitution>
      <xsl:apply-templates/>
    </rdf:RDF>
  </xsl:template>

  <xsl:variable name="columns">
    <xsl:for-each select="//tei:row[1]/tei:cell">
      <column index="position()" name="{ex:slugify(text())}"/>
    </xsl:for-each>
  </xsl:variable>

  <xsl:template match="*|@*|text()" mode="#all"/>
  <xsl:template match="row/*/text()">
    <xsl:copy-of select="."/>
  </xsl:template>

  <xsl:template match="tei:*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="tei:table">
    <xsl:apply-templates select="tei:row[position() gt 1]"/>
  </xsl:template>

  <xsl:template match="tei:row">
    <xsl:variable name="row">
      <row id="{position()}">
        <xsl:for-each select="tei:cell">
          <xsl:variable name="i" select="position()"/>
          <xsl:variable name="x" select="$columns/column[position()=$i]"/>
          <xsl:if test="text() and $x">
            <xsl:element name="{$x/@name}">
              <xsl:value-of select="text()"/>
            </xsl:element>
          </xsl:if>
        </xsl:for-each>
      </row>
    </xsl:variable>
    <xsl:apply-templates select="$row/row"/>
  </xsl:template>

  <xsl:template match="row">
    <xsl:variable name="type">
      <xsl:choose>
        <xsl:when test="ex:slugify(type)='equipment'">oo:Equipment</xsl:when>
        <xsl:when test="ex:slugify(type)='facility'">oo:Facility</xsl:when>
        <xsl:when test="not(type)">oo:Equipment</xsl:when>
        <xsl:otherwise>
          <xsl:message terminate="yes">Unexpected type: <xsl:value-of select="ex:slugify(type)"/>.</xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="uri">
      <xsl:value-of select="concat($base-uri, if (type) then ex:slugify(type) else 'equipment', '/', if (id) then ex:slugify(id/text()) else @id)"/>
    </xsl:variable>
    <xsl:element name="{$type}">
      <xsl:attribute name="rdf:about" select="$uri"/>
      <oo:formalOrganization rdf:resource="{$provider-uri}"/>
      <xsl:apply-templates>
        <xsl:with-param name="uri" select="$uri"/>
      </xsl:apply-templates>
      <oo:contact>
        <foaf:Agent rdf:about="{$uri}/contact">
          <xsl:apply-templates mode="contact">
            <xsl:with-param name="uri" select="$uri"/>
          </xsl:apply-templates>
        </foaf:Agent>
      </oo:contact>
    </xsl:element>
  </xsl:template>

  <xsl:template match="name">
    <rdfs:label><xsl:apply-templates/></rdfs:label>
  </xsl:template>

  <xsl:template match="description">
    <rdfs:comment><xsl:apply-templates/></rdfs:comment>
  </xsl:template>

  <xsl:template match="related-facility-id">
    <oo:facility rdf:resource="{$base-uri}facility/{ex:slugify(text())}"/>
  </xsl:template>

  <xsl:template match="contact-name" mode="contact">
    <foaf:name><xsl:apply-templates/></foaf:name>
  </xsl:template>

  <xsl:template match="contact-email" mode="contact">
    <v:email rdf:resource="mailto:{text()}"/>
  </xsl:template>

  <xsl:template match="site-location">
    <xsl:variable name="dbpedia">
      <xsl:choose>
        <xsl:when test="text()='South Kensington'">South_Kensington</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$dbpedia">
        <foaf:based_near>
          <geo:SpatialThing rdf:about="http://dbpedia.org/resource/{$dbpedia}">
            <rdfs:label>
              <xsl:apply-templates/>
            </rdfs:label>
          </geo:SpatialThing>
        </foaf:based_near>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>Unexpected site location: <xsl:value-of select="text()"/></xsl:message>
        <foaf:based_near>
          <geo:SpatialThing rdf:about="{$base-uri}site-location/{ex:slugify(text())}">
            <rdfs:label>
              <xsl:apply-templates/>
            </rdfs:label>
          </geo:SpatialThing>
        </foaf:based_near>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
     
  <xsl:template match="building">
    <spatialrelations:within>
      <rooms:Building rdf:about="{$base-uri}building/{ex:slugify(text())}">
        <rdfs:label>
          <xsl:apply-templates/>
        </rdfs:label>
      </rooms:Building>
    </spatialrelations:within>
  </xsl:template>

  <xsl:template match="web-address">
    <foaf:page rdf:resource="{text()}"/>
  </xsl:template>
</xsl:stylesheet>
