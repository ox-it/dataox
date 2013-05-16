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


  <xsl:template match="list[@name='Service classifications']">
    <skos:ConceptScheme rdf:about="{$service-classification-base-uri}">
      <skos:prefLabel>X-Ray Service Classification</skos:prefLabel>
      <dcterms:publisher>
        <org:FormalOrganization rdf:about="http://id.ja.net/">
          <rdfs:label>Janet</rdfs:label>
          <foaf:homepage rdf:resource="http://www.ja.net/"/>
        </org:FormalOrganization>
      </dcterms:publisher>
      <xsl:apply-templates/>
    </skos:ConceptScheme>
  </xsl:template>

  <xsl:template match="list[@name='Service classifications']/rows/row">
    <skos:hasTopConcept>
      <skos:Concept rdf:about="{ex:service-classification-uri(.)}">
        <xsl:apply-templates/>
        <skos:inScheme rdf:resource="{$service-classification-base-uri}"/>
      </skos:Concept>
    </skos:hasTopConcept>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]">
    <skos:prefLabel>
      <xsl:value-of select="."/>
    </skos:prefLabel>
  </xsl:template>

  <xsl:template match="field[@name='Description']/text[text()]">
    <skos:definition>
      <xsl:value-of select="."/>
    </skos:definition>
  </xsl:template>

</xsl:stylesheet>
