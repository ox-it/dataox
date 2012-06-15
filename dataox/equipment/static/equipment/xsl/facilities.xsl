<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oo="http://purl.org/openorg/"
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
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:humfrey="http://purl.org/NET/humfrey/ns/"
    xmlns:org="http://www.w3.org/ns/org#"
  >
  <xsl:output method="xml" indent="yes"/>
  <xsl:param name="store" select="'public'"/>

  <xsl:function name="ex:slugify">
    <xsl:param name="term"/>
    <xsl:choose>
      <xsl:when test="contains($term, '(')">
        <xsl:value-of select="ex:slugify(substring-before($term, '('))"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="replace(lower-case(normalize-space($term)), '[^a-z0-9]+', '-')"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <xsl:variable name="columns">
    <columns>
      <xsl:for-each select="//tei:row[1]/tei:cell">
        <column name="{text()}" slug="{ex:slugify(text())}" n="{position()}"/>
      </xsl:for-each>
    </columns>
  </xsl:variable>
  <xsl:key name="columns" match="column" use="number(@n)"/>

  <xsl:template match="/">
    <xsl:variable name="facilities">
      <xsl:apply-templates select="//tei:table[1]/tei:row[position() &gt; 1]" mode="preprocess"/>
    </xsl:variable>
    <rdf:RDF>
      <xsl:apply-templates select="$facilities/facility"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="tei:row" mode="preprocess">
    <facility uri="https://data.ox.ac.uk/id/facility/{count(preceding-sibling::tei:row)}">
      <xsl:for-each select="tei:cell">
        <xsl:if test="text()">
          <xsl:element name="{key('columns', position(), $columns)/@slug}">
            <xsl:value-of select="normalize-space(text())"/>
          </xsl:element>
        </xsl:if>
      </xsl:for-each>
    </facility>
  </xsl:template>

  <xsl:template match="facility">
    <oo:Facility rdf:about="{@uri}">
      <xsl:apply-templates select="*"/>
    </oo:Facility>
  </xsl:template>

  <xsl:template match="name-of-facility-service">
    <rdfs:label>
      <xsl:value-of select="text()"/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="department">
    <oo:facilityOf>
      <org:Organization rdf:about="https://data.ox.ac.uk/id/facility-department/{ex:slugify(text())}">
        <humfrey:searchNormalization rdf:parseType="Resource">
          <humfrey:searchQuery>
            <xsl:value-of select="text()"/>
          </humfrey:searchQuery>
          <humfrey:searchType>organization</humfrey:searchType>
        </humfrey:searchNormalization>
      </org:Organization>
    </oo:facilityOf>
  </xsl:template>
  <xsl:template match="*"/>
</xsl:stylesheet>
