<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:oo="http://purl.org/openorg/"
    xmlns:org="http://www.w3.org/ns/org#"
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

  <xsl:param name="store"/>
  <xsl:variable name="internal" select="$store='itservices'"/>

  <xsl:template match="list[@name='User Information List']/rows/row">
    <xsl:variable name="content-type" select=".//field[@name='ContentType']/text/text()"/>
    <xsl:if test="$content-type = 'DomainGroup' and starts-with(.//field[@name='Name']/text, 'AD-OAK\group_')">
      <foaf:Group rdf:about="{ex:agent-uri(.)}">
        <rdf:type rdf:resource="http://purl.org/goodrelations/v1#BusinessEntityType"/>
        <xsl:apply-templates mode="in-domain-group"/>
      </foaf:Group>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text" mode="in-domain-group">
    <foaf:name>
      <xsl:value-of select="substring-before(., ' Group')"/>
    </foaf:name>
  </xsl:template>
</xsl:stylesheet>

