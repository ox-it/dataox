<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
  <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#">
  <!ENTITY xhtml "http://www.w3.org/1999/xhtml">
  <!ENTITY xtypes "http://purl.org/xtypes/">
]>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xhtml="http://www.w3.org/1999/xhtml#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:event="http://purl.org/NET/c4dm/event.owl#"
    xmlns:prog="http://purl.org/prog/"
    xmlns:tl="http://purl.org/NET/c4dm/timeline.owl#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:mlo="http://purl.org/net/mlo/"
    xmlns:xmlo="http://purl.org/net/mlo"
    xmlns:xcri="http://xcri.org/profiles/1.2/"
    xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    xmlns:time="http://www.w3.org/2006/time#"
    xmlns:ex="http://www.example.org/"
    xmlns:humfrey="http://purl.org/NET/humfrey/ns/"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="base">https://course.data.ox.ac.uk/id/careers/</xsl:variable>
  <xsl:param name="store">public</xsl:param>

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
    <xsl:variable name="data">
      <rows>
        <xsl:apply-templates select="/tei:TEI/tei:text/tei:body/tei:table/tei:row[position() &gt; 1]" mode="preprocess"/>
      </rows>
    </xsl:variable>
    <rdf:RDF>
      <xcri:catalog rdf:about="{$base}catalogue">
        <rdfs:label>Courses from the Careers Service at the University of Oxford</rdfs:label>
        <dcterms:publisher>
          <rdf:Resource  rdf:about="http://oxpoints.oucs.ox.ac.uk/id/23233545">
            <xsl:for-each select="$data/rows/row">
              <mlo:offers rdf:resource="{$base}course/{course-code/text()}"/>
            </xsl:for-each>
          </rdf:Resource>
        </dcterms:publisher>
        <xsl:for-each select="$data/rows/row">
          <skos:member>
            <xsl:apply-templates select="."/>
          </skos:member>
        </xsl:for-each>
      </xcri:catalog>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="tei:row" mode="preprocess">
    <row>
      <xsl:for-each select="tei:cell">
        <xsl:if test="*|@*|text()">
          <xsl:element name="{if (string-length(key('columns', position(), $columns)/@slug)) then key('columns', position(), $columns)/@slug else 'column'}">
            <xsl:copy-of select="*|@*|text()"/>
          </xsl:element>
        </xsl:if>
      </xsl:for-each>
    </row>
  </xsl:template>

  <xsl:template match="row">
    <xcri:course rdf:about="{$base}course/{course-code/text()}">
      <xsl:apply-templates select="*[text()]"/>
    </xcri:course>
  </xsl:template>

  <xsl:template match="course-title">
    <rdfs:label>
      <xsl:value-of select="text()"/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="course-description">
    <dcterms:description>
      <xsl:value-of select="text()"/>
    </dcterms:description>
  </xsl:template>

<!-- We have bad data for this one
  <xsl:template match="url">
    <foaf:homepage>
      <xsl:value-of select="text()"/>
    </foaf:homepage>
  </xsl:template>
-->

  <xsl:template match="course-code">
    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/careers-course">
      <xsl:value-of select="text()"/>
    </skos:notation>
  </xsl:template>

  <xsl:template match="skills">
    <dcterms:subject rdf:resource="https://data.ox.ac.uk/id/ox-rdf/descriptor/{text()}"/>
  </xsl:template>

  <xsl:template match="abstract">
    <xcri:abstract>
      <xsl:value-of select="text()"/>
    </xcri:abstract>
  </xsl:template>

  <xsl:template match="venue-text">
    <mlo:specifies>
      <xcri:presentation rdf:about="{$base}presentation/{../course-code/text()}">
        <xsl:apply-templates select="../*" mode="presentation"/>
      </xcri:presentation>
    </mlo:specifies>
  </xsl:template>

  <xsl:template match="venue-text" mode="presentation">
    <xcri:venue>
      <geo:SpatialThing rdf:about="{$base}venue/{../course-code/text()}">
        <rdfs:label>
          <xsl:value-of select="text()"/>
        </rdfs:label>
        <humfrey:searchNormalization rdf:parseType="Resource">
          <humfrey:searchType>spatial-thing</humfrey:searchType>
          <humfrey:searchQuery><xsl:value-of select="text()"/></humfrey:searchQuery>
        </humfrey:searchNormalization>
      </geo:SpatialThing>
    </xcri:venue>
  </xsl:template>

  <xsl:template match="*" mode="#all"/>
</xsl:stylesheet>
