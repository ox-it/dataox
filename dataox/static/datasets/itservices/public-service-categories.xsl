<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:oo="http://purl.org/openorg/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:tio="http://purl.org/tio/ns#"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    xmlns:ex="http://www.example.org/"
    xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
    xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
    xpath-default-namespace="https://github.com/ox-it/python-sharepoint/"
    version="2.0">
  <xsl:import href="common.xsl"/>
  <xsl:output method="xml" indent="yes"/>



  <xsl:template match="list[@name='Public Service Categories']/rows">
    <skos:ConceptScheme rdf:about="{$service-category-base-uri}">
      <skos:prefLabel xml:lang="en">Categories for the IT Services public Service Catalogue</skos:prefLabel>
      <xsl:apply-templates/>
    </skos:ConceptScheme>

    <xsl:for-each select=".//field[@name='Services']/lookup">
      <rdf:Description rdf:about="{ex:service-uri('service', key('services', @id))}">
        <dcterms:subject rdf:resource="{$service-category-base-uri}/{../../field[@name='Slug']/text/text()}"/>
      </rdf:Description>
    </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="field[@name='Featured_x0020_Services']/text[text()]">
    <xsl:variable name="tree" select="/"/>
    <adhoc:featuredList rdf:parseType="Collection">
      <xsl:for-each select="tokenize(text(), '\s+')">
        <xsl:variable name="service" select="key('services-by-slug', ., $tree)"/>
        <xsl:choose>
          <xsl:when test="$service">
            <rdf:Description rdf:about="{ex:service-uri('service', $service)}"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:message>Unexpected service slug: <xsl:value-of select="."/></xsl:message>
          </xsl:otherwise> 
        </xsl:choose>
      </xsl:for-each>
    </adhoc:featuredList>
  </xsl:template>

  <xsl:template match="list[@name='Public Service Categories']/rows/row">
    <skos:hasTopConcept>
      <skos:Concept rdf:about="{$service-category-base-uri}/{.//field[@name='Slug']/text/text()}">
        <xsl:apply-templates/>
        <skos:inScheme rdf:resource="{$service-category-base-uri}"/>
      </skos:Concept>
    </skos:hasTopConcept>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]">
    <skos:prefLabel xml:lang="en">
      <xsl:value-of select="text()"/>
    </skos:prefLabel>
  </xsl:template>

  <xsl:template match="field[@name='Description']/text[text()]">
    <skos:definition xml:lang="en">
      <xsl:value-of select="text()"/>
    </skos:definition>
  </xsl:template>

  <xsl:template match="field[@name='FontAwesome']/text[text()]">
    <adhoc:fontAwesome>
      <xsl:value-of select="text()"/>
    </adhoc:fontAwesome>
  </xsl:template>

  <xsl:template match="field[@name='Slug']/text[text()]">
    <skos:notation rdf:datatype="https://id.it.ox.ac.uk/notation/service-category">
      <xsl:value-of select="text()"/>
    </skos:notation>
  </xsl:template>
</xsl:stylesheet>
