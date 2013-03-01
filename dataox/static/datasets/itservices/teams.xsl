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

  <xsl:template match="site">
    <xsl:if test="$internal">
      <xsl:apply-imports/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="list[@name='Teams']/rows/row">
    <xsl:if test="not(fields/field[@name='URI']/text/text())">
      <org:OrganizationalUnit rdf:about="{ex:team-uri(.)}">
        <xsl:apply-templates/>
      </org:OrganizationalUnit>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]">
    <rdfs:label>
      <xsl:value-of select="."/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="field[@name='Description']/text[text()]">
    <rdfs:comment>
      <xsl:value-of select="."/>
    </rdfs:comment>
  </xsl:template>

  <xsl:template match="field[@name='E_x002d_mail_x0020_address']/text/text()">
    <v:email rdf:resource="mailto:{.}"/>
  </xsl:template>

  <xsl:template match="field[@name='Part_x0020_of']/lookup">
    <org:subOrganizationOf rdf:resource="{ex:team-uri(key('teams', @id))}"/>
  </xsl:template>

  <xsl:template match="field[@name='Telephone_x0020_extension']/text/text()">
    <xsl:call-template name="telephone-extension"/>
  </xsl:template>
</xsl:stylesheet>
