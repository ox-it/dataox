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

  <xsl:template name="uri"/>

  <xsl:template match="tei:row" mode="preprocess">
    <xsl:element name="{$type}">
      <xsl:attribute name="uri">
        <xsl:call-template name="uri"/>
      </xsl:attribute>
      <xsl:for-each select="tei:cell">
        <xsl:if test="text()">
          <xsl:element name="{key('columns', position(), $columns)/@slug}">
            <xsl:value-of select="normalize-space(text())"/>
          </xsl:element>
        </xsl:if>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>


  <!-- These are columns common among both equipment and facilities -->

  <xsl:template match="shareable" mode="outside">
    <xsl:choose>
      <xsl:when test="text()='Y'">
        <gr:Offering rdf:about="{../@uri}/offering">
          <rdfs:label>Available for use by members of the University of Oxford</rdfs:label>
          <tio:incudes>
            <tio:TicketPlaceholder rdf:about="{../@uri}/the-use-thereof">
              <tio:accessTo rdf:resource="{../@uri}"/>
            </tio:TicketPlaceholder>
          </tio:incudes>
          <gr:eligibleCustomerTypes rdf:resource="https://data.ox.ac.uk/id/group/member"/>
        </gr:Offering>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="shareable" mode="inside">
    <adhoc:equipment-shareability>
      <xsl:attribute name="rdf:resource">
        <xsl:text>https://data.ox.ac.uk/id/equipment-shareability/</xsl:text>
        <xsl:choose>
          <xsl:when test="text()='Y'">yes</xsl:when>
          <xsl:when test="text()='C'">contact</xsl:when>
          <xsl:when test="text()='N'">no</xsl:when>
        </xsl:choose>
      </xsl:attribute>
    </adhoc:equipment-shareability>
  </xsl:template>

  <xsl:template match="subcategory" mode="inside">
    <dcterms:subject rdf:resource="https://data.ox.ac.uk/id/equipment-category/{ex:slugify(../category)}/{ex:slugify(.)}"/>
  </xsl:template>

  <xsl:template match="availability" mode="inside">
    <oo:availability>
      <oo:Availability rdf:about="{../@uri}/availability">
        <rdfs:label><xsl:value-of select="text()"/></rdfs:label>
      </oo:Availability>
    </oo:availability>
  </xsl:template>

  <xsl:template match="access" mode="inside">
    <oo:accessPrerequisite>
      <oo:AccessPrerequisite rdf:about="{../@uri}/access-prerequisite">
        <rdfs:label><xsl:value-of select="text()"/></rdfs:label>
      </oo:AccessPrerequisite>
    </oo:accessPrerequisite>
  </xsl:template>
    
  <xsl:template match="restrictions-on-use" mode="inside">
    <oo:useRestriction>
      <oo:UseRestriction rdf:about="{../@uri}/use-restriction">
        <rdfs:label><xsl:value-of select="text()"/></rdfs:label>
      </oo:UseRestriction>
    </oo:useRestriction>
  </xsl:template>

  <xsl:template match="website" mode="inside">
    <xsl:choose>
      <xsl:when test="matches(text(), '^(http|https|ftp)://')">
        <foaf:page rdf:resource="{.}"/>
      </xsl:when>
      <xsl:when test="starts-with(text(), 'www.')">
        <foaf:page rdf:resource="http://{.}"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="image-url" mode="inside">
    <xsl:choose>
      <xsl:when test="matches(text(), '^(http|https|ftp)://')">
        <foaf:depiction>
           <foaf:Image rdf:about="{.}"/>
        </foaf:depiction>
      </xsl:when>
      <xsl:when test="starts-with(text(), 'www.')">
        <foaf:depiction>
           <foaf:Image rdf:about="http://{.}"/>
        </foaf:depiction>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="department-code" mode="inside">
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

  <xsl:template match="building-number" mode="inside">
    <spatialrelations:within>
      <rdf:Resource rdf:about="https://data.ox.ac.uk/equipment-building/{ex:slugify(text())}">
        <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/estates">
          <xsl:value-of select="text()"/>
        </skos:notation>
      </rdf:Resource>
    </spatialrelations:within>
  </xsl:template>

  <xsl:template match="*" mode="skos inside outside"/>
</xsl:stylesheet>
