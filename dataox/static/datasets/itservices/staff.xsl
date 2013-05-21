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

  <xsl:function name="ex:post-uri">
    <xsl:param name="node"/>
    <xsl:text>https://data.ox.ac.uk/id/itservices/post/</xsl:text>
    <xsl:value-of select="$node/ancestor-or-self::row[1]/@id"/>
  </xsl:function>

  <xsl:template match="list[@name='User Information List']/rows/row">
    <xsl:variable name="content-type" select=".//field[@name='ContentType']/text/text()"/>
    <xsl:if test="$content-type = 'Person'">
      <foaf:Person rdf:about="{ex:agent-uri(.)}">
        <xsl:apply-templates mode="in-person"/>
      </foaf:Person>
    </xsl:if>
  </xsl:template>

  <xsl:template match="list[@name='Staff']/rows/row">
    <org:Post rdf:about="{ex:post-uri(.)}">
      <xsl:apply-templates mode="in-post"/>
    </org:Post>
    <xsl:apply-templates mode="outside-post"/>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text" mode="in-person">
    <foaf:name>
      <xsl:value-of select="."/>
    </foaf:name>
  </xsl:template>

  <xsl:template match="field[@name='FirstName']/text" mode="in-person">
    <foaf:firstName>
      <xsl:value-of select="."/>
    </foaf:firstName>
  </xsl:template>

  <xsl:template match="field[@name='LastName']/text" mode="in-person">
    <foaf:lastName>
      <xsl:value-of select="."/>
    </foaf:lastName>
  </xsl:template>

  <xsl:template match="field[@name='Picture']/url[@href]" mode="in-person">
    <foaf:depiction>
      <foaf:Image rdf:about="{@href}"/>
    </foaf:depiction>
  </xsl:template>

  <xsl:template match="field[@name='EMail']/text" mode="in-person">
    <foaf:mbox rdf:resource="mailto:{.}"/>
  </xsl:template>

  <xsl:template match="field[@name='WorkPhone']/text/text()" mode="in-person">
    <xsl:call-template name="telephone-extension"/>
  </xsl:template>

  <xsl:template match="field[@name='Role']/text[text()]" mode="in-post">
    <org:role>
      <org:Role rdf:about="{ex:post-uri(.)}/role">
        <skos:prefLabel>
          <xsl:value-of select="."/>
        </skos:prefLabel>
      </org:Role>
    </org:role>
  </xsl:template>

  <xsl:template match="field[@name='Person']/user" mode="in-post">
    <org:member rdf:resource="{ex:agent-uri(.)}"/>
  </xsl:template>

  <xsl:template match="field[@name='Team']/lookup" mode="in-post">
    <org:organization rdf:resource="{ex:team-uri(key('teams', @id))}"/>
  </xsl:template>

  <xsl:template match="field[@name='Manager']/boolean" mode="outside-post">
    <xsl:variable name="team-uri" select="ex:team-uri(key('teams', ../../field[@name='Team']/lookup/@id))"/>
    <rdf:Description rdf:about="{ex:agent-uri(../../field[@name='Person']/user)}">
      <xsl:choose>
        <xsl:when test="text()='true'">
          <org:headOf rdf:resource="{$team-uri}"/>
        </xsl:when>
        <xsl:when test="text()='false'">
          <org:memberOf rdf:resource="{$team-uri}"/>
        </xsl:when>
      </xsl:choose>
    </rdf:Description>
  </xsl:template>

  <xsl:template match="field[@name='Office']/text" mode="in-post">
    <org:basedAt>
      <xsl:attribute name="rdf:resource">
        <xsl:text>http://oxpoints.oucs.ox.ac.uk/id/</xsl:text>
        <xsl:choose>
          <xsl:when test="text()='Banbury Road'">40002001</xsl:when>
          <xsl:when test="text()='Blue Boar Court'">23233619</xsl:when>
          <xsl:when test="text()='Hythe Bridge Street'">23233672</xsl:when>
          <xsl:when test="text()='Malthouse'">23233636</xsl:when>
          <xsl:when test="text()='Wellington Square'">23233665</xsl:when>
          <xsl:when test="text()='Worcester Street'">23233614</xsl:when>
        </xsl:choose>
      </xsl:attribute>
    </org:basedAt>
  </xsl:template>
</xsl:stylesheet>
