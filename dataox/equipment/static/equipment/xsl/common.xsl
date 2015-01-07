<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oo="http://purl.org/openorg/"
    xmlns:cat="http://purl.org/NET/catalog/"
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
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
  >

  <xsl:param name="store" select="'public'"/>
  <xsl:variable name="type" select="'rdf:Resource'"/>
  <xsl:variable name="group-column"/>
  <xsl:variable name="catalog-uri"/>
  <xsl:output method="xml" indent="yes"/>

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

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates select="." mode="in-rdf"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="/" mode="in-rdf">
    <xsl:variable name="items">
      <xsl:for-each-group select="//tei:table[1]/tei:row[position() &gt; 1]" group-by="if ($group-column) then tei:cell[xs:integer($group-column)] else position()">
        <xsl:call-template name="preprocess"/>
      </xsl:for-each-group>
    </xsl:variable>
    <rdf:Description rdf:about="https://data.ox.ac.uk/id/dataset/research-facilities">
      <void:subset>
        <cat:Catalog rdf:about="{$catalog-uri}">
          <rdf:type rdf:resource="http://rdfs.org/ns/void#Dataset"/>
          <xsl:apply-templates select="$items" mode="in-catalog"/>
          <oo:organization rdf:resource="http://oxpoints.oucs.ox.ac.uk/id/00000000"/>
        </cat:Catalog>
      </void:subset>
    </rdf:Description>
    <xsl:apply-templates select="$items/item" mode="record"/>
  </xsl:template>

  <xsl:template match="/" mode="in-catalog">
    <xsl:apply-templates mode="catalog-record-links"/>
  </xsl:template>

  <xsl:template match="item" mode="catalog-record-links">
    <xsl:if test="@to-include='Yes' or $store='public'">
      <cat:item rdf:resource="{@uri}"/>
      <cat:record rdf:resource="{@record-uri}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="item" mode="record">
    <!-- This expects three columns per row called "Public", "University" and "SEESEC", each
         containing either "Yes" or "No". $store is passed in as a parameter to the template
         and decided which of these columns will be used.

         The public target is slightly special. We say that everything exists, just not what
         it is. It also does not get any contact details.
    -->

    <xsl:if test="@to-include='Yes' or $store='public'">
      <cat:CatalogRecord rdf:about="{@record-uri}">
        <foaf:primaryTopic>
	  <xsl:apply-templates select="." mode="item"/>
        </foaf:primaryTopic>
      </cat:CatalogRecord>
      <xsl:if test="@to-include='Yes'">
        <xsl:apply-templates select="*|row/*" mode="outside"/>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <xsl:template match="item" mode="item">
    <xsl:element name="{$type}">
      <xsl:attribute name="rdf:about">
        <xsl:value-of select="@uri"/>
      </xsl:attribute>

      <!-- Everything is part of the University of Oxford -->
      <oo:formalOrganization rdf:resource="http://oxpoints.oucs.ox.ac.uk/id/00000000"/>

      <xsl:if test="@to-include='Yes'">
        <xsl:apply-templates select="*|row/*" mode="inside"/>
      </xsl:if>
    </xsl:element>
  </xsl:template>

  <xsl:variable name="columns">
    <xsl:for-each select="//tei:row[1]/tei:cell">
      <column name="{text()}" slug="{ex:slugify(text())}" n="{position()}"/>
    </xsl:for-each>
  </xsl:variable>
  <xsl:key name="columns" match="column" use="number(@n)"/>

  <xsl:template name="uri"/>
  <xsl:template name="record-uri"/>

  <xsl:template name="preprocess">
    <item>
      <xsl:attribute name="record-uri">
        <xsl:call-template name="record-uri"/>
      </xsl:attribute>
      <xsl:attribute name="uri">
        <xsl:call-template name="uri"/>
      </xsl:attribute>
      <xsl:attribute name="to-include">
        <xsl:choose>
          <xsl:when test="$store='public'"><xsl:value-of select="tei:cell[position() = $columns/column[@slug='public']/@n]"/></xsl:when>
          <xsl:when test="$store='equipment'"><xsl:value-of select="tei:cell[position() = $columns/column[@slug='university']/@n]"/></xsl:when>
          <xsl:when test="$store='seesec'"><xsl:value-of select="tei:cell[position() = $columns/column[@slug='seesec']/@n]"/></xsl:when>
          <xsl:otherwise>
            <xsl:message terminate="yes">Unexpected store: <xsl:value-of select="$store"/></xsl:message>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:for-each select="tei:cell">
        <xsl:if test="node() and key('columns', position(), $columns)/@slug">
          <xsl:element name="{key('columns', position(), $columns)/@slug}">
            <xsl:copy-of select="node()"/>
          </xsl:element>
        </xsl:if>
      </xsl:for-each>
      <xsl:for-each select="current-group()">
        <row>
          <xsl:for-each select="tei:cell">
            <xsl:if test="text()">
              <xsl:element name="{key('columns', position(), $columns)/@slug}">
                <xsl:copy-of select="node()"/>
              </xsl:element>
            </xsl:if>
          </xsl:for-each>
        </row>
      </xsl:for-each>
    </item>
  </xsl:template>


  <!-- These are columns common among both equipment and facilities -->

  <xsl:template match="item/shareable" mode="outside">
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

  <xsl:template match="item/shareable" mode="inside">
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

  <xsl:template match="row/subcategory" mode="inside">
    <dcterms:subject>
      <skos:Concept rdf:about="https://data.ox.ac.uk/id/unmatched-equipment-category/{ex:slugify(../category)}/{ex:slugify(.)}">
        <skos:prefLabel>
          <xsl:value-of select="text()"/>
        </skos:prefLabel>
        <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/equipment-category">
          <xsl:value-of select="concat(ex:slugify(../category), '/', ex:slugify(.))"/>
        </skos:notation>
      </skos:Concept>
    </dcterms:subject>
  </xsl:template>

  <xsl:template match="item/availability" mode="inside">
    <oo:availability>
      <oo:Availability rdf:about="{../@uri}/availability">
        <rdfs:label><xsl:value-of select="text()"/></rdfs:label>
      </oo:Availability>
    </oo:availability>
  </xsl:template>

  <xsl:template match="item/access" mode="inside">
    <oo:accessPrerequisite>
      <oo:AccessPrerequisite rdf:about="{../@uri}/access-prerequisite">
        <rdfs:label><xsl:value-of select="text()"/></rdfs:label>
      </oo:AccessPrerequisite>
    </oo:accessPrerequisite>
  </xsl:template>
    
  <xsl:template match="item/restrictions-on-use" mode="inside">
    <oo:useRestriction>
      <oo:UseRestriction rdf:about="{../@uri}/use-restriction">
        <rdfs:label><xsl:value-of select="text()"/></rdfs:label>
      </oo:UseRestriction>
    </oo:useRestriction>
  </xsl:template>

  <xsl:template match="item/website" mode="inside">
    <xsl:choose>
      <xsl:when test="matches(text(), '^(http|https|ftp)://')">
        <foaf:page rdf:resource="{.}"/>
      </xsl:when>
      <xsl:when test="starts-with(text(), 'www.')">
        <foaf:page rdf:resource="http://{.}"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="item/image-url" mode="inside">
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

  <xsl:template match="item/department-code" mode="inside">
    <oo:organizationPart>
      <org:Organization rdf:about="https://data.ox.ac.uk/id/equipment-department/{ex:slugify(text())}">
        <xsl:apply-templates select="text()" mode="department-code-notation"/>
        <rdfs:label>
          <xsl:value-of select="../department/normalize-space(text())"/>
        </rdfs:label>
      </org:Organization>
    </oo:organizationPart>
  </xsl:template>

  <xsl:template match="text()" mode="department-code-notation">
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
  </xsl:template>

  <xsl:template match="item/building-number" mode="inside">
    <spatialrelations:within>
      <rdf:Resource rdf:about="https://data.ox.ac.uk/equipment-building/{ex:slugify(text())}">
        <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/estates">
          <xsl:value-of select="text()"/>
        </skos:notation>
      </rdf:Resource>
    </spatialrelations:within>
  </xsl:template>

  <xsl:template match="*" mode="xhtml-or-text">
    <xsl:param name="name"/>
    <xsl:element name="{$name}">
      <xsl:if test="xhtml:div">
        <xsl:attribute name="rdf:datatype">http://purl.org/xtypes/Fragment-XHTML</xsl:attribute>
        <xsl:attribute name="rdf:parseType">Literal</xsl:attribute>
      </xsl:if>
      <xsl:copy-of select="node()" copy-namespaces="no"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="*" mode="skos inside outside"/>
</xsl:stylesheet>
