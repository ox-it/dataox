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
    xpath-default-namespace="https://github.com/ox-it/python-sharepoint/"
    version="2.0">
  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="*" mode="#all">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  <xsl:template match="text()|@*" mode="#all"/>
  
  <xsl:template match="list[@name='Licenses']/rows/row">
    <dcterms:LicenseDocument rdf:about="{fields/field[@name='URI']/url/@href}">
      <rdf:type rdf:resource="http://creativecommons.org/ns#License"/>
      <xsl:apply-templates select="fields/field"/>
    </dcterms:LicenseDocument>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]">
    <dcterms:title>
      <xsl:value-of select="text()"/>
    </dcterms:title>
    <rdfs:label>
      <xsl:value-of select="text()"/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="field[@name='Logo']/url">
    <foaf:logo rdf:resource="{@href}"/>
  </xsl:template>
</xsl:stylesheet>
