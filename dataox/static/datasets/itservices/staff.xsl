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
    xmlns:humfrey="http://purl.org/NET/humfrey/ns/"
    xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:spatialrelations="http://data.ordnancesurvey.co.uk/ontology/spatialrelations/"
    xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
    xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
    xpath-default-namespace="https://github.com/ox-it/python-sharepoint/"
    version="2.0">
  <xsl:import href="common.xsl"/>
  <xsl:output method="xml" indent="yes"/>

  <xsl:key name="post-holders" match="list[@name='Staff']/rows/row" use="fields/field[@name='Person']/user/@id"/>
  <xsl:key name="team-managers" match="list[@name='Staff']/rows/row[.//field[@name='Manager']/boolean/text()='true']" use="fields/field[@name='Team']/lookup/@id"/>
  
  <xsl:key name="staff" match="list[@name='Staff']/rows/row" use="@id"/>
  <xsl:key name="teams" match="list[@name='Teams']/rows/row" use="@id"/>

  <xsl:template match="site">
      <xsl:apply-imports/>
  </xsl:template>


  <xsl:template match="list[@name='User Information List']/rows/row">
    <xsl:variable name="content-type" select=".//field[@name='ContentType']/text/text()"/>
    <xsl:variable name="username" select=".//field[@name='UserName']/text/text()"/>
    <xsl:if test="$content-type = 'Person' and $username and ex:include-person(.)">
      <foaf:Person rdf:about="{ex:agent-uri(.)}">
        <xsl:apply-templates mode="in-person"/>
        <xsl:variable name="post" select="key('post-holders', @id)"/>
        <xsl:for-each select="$post">
          <org:holds rdf:resource="{ex:post-uri(.)}"/>
          <xsl:variable name="team-uri" select="ex:team-uri(key('teams', fields/field[@name='Team']/lookup/@id))"/>
          <xsl:choose>
            <xsl:when test="fields/field[@name='Manager']/text/text()='true'">
              <org:headOf rdf:resource="{$team-uri}"/>
            </xsl:when>
            <xsl:otherwise>
              <org:memberOf rdf:resource="{$team-uri}"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
      </foaf:Person>
    </xsl:if>
  </xsl:template>

  <xsl:template match="list[@name='Staff']/rows/row">
    <xsl:if test="ex:include-person(fields/field[@name='Person']/user)">
    <org:Post rdf:about="{ex:post-uri(.)}">
      <xsl:apply-templates mode="in-post"/>
      <xsl:if test="not(.//field[@name='Manager0'])">
        <xsl:apply-templates select="." mode="infer-manager"/>
      </xsl:if>
    </org:Post>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text" mode="in-person">
    <foaf:name>
      <xsl:value-of select="."/>
    </foaf:name>
    <xsl:if test="not(../../field[@name='FirstName']/text/text())">
      <foaf:firstName>
        <xsl:value-of select="substring-before(., ' ')"/>
      </foaf:firstName>
    </xsl:if>
    <xsl:if test="not(../../field[@name='LastName']/text/text())">
      <foaf:lastName>
        <xsl:value-of select="substring-after(., ' ')"/>
      </foaf:lastName>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='FirstName']/text[text()]" mode="in-person">
    <foaf:firstName>
      <xsl:value-of select="."/>
    </foaf:firstName>
  </xsl:template>

  <xsl:template match="field[@name='LastName']/text[text()]" mode="in-person">
    <foaf:lastName>
      <xsl:value-of select="."/>
    </foaf:lastName>
  </xsl:template>

  <xsl:template match="field[@name='Picture']/url[@href]" mode="in-person">
    <xsl:if test="$internal">
      <xsl:variable name="username" select="../../field[@name='UserName']/text"/>
      <foaf:img>
        <foaf:Image rdf:about="https://backstage.data.ox.ac.uk/sharepoint/user-profile-image/{$username}/large/">
          <foaf:thumbnail>
            <foaf:Image rdf:about="https://backstage.data.ox.ac.uk/sharepoint/user-profile-image/{$username}/medium/"/>
          </foaf:thumbnail>
        </foaf:Image>
      </foaf:img>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='EMail']/text" mode="in-person">
    <foaf:mbox rdf:resource="mailto:{.}"/>
  </xsl:template>

  <xsl:template match="field[@name='WorkPhone']/text/text()" mode="in-person">
    <xsl:call-template name="telephone-extension"/>
  </xsl:template>
  
  <xsl:template match="field[@name='Title']/text" mode="in-post">
    <rdfs:label>
      <xsl:choose>
        <xsl:when test="../../field[@name='Person']">
          <xsl:value-of select="key('users', ../../field[@name='Person']/user/@id)//field[@name='Title']/text"/>
        </xsl:when>
        <xsl:otherwise>vacancy</xsl:otherwise>
      </xsl:choose>
      <xsl:text> (</xsl:text>
      <xsl:value-of select="../../field[@name='Role']/text"/>
      <xsl:text>)</xsl:text>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="field[@name='Role']/text" mode="in-post">
    <org:role>
      <org:Role rdf:about="{ex:post-uri(.)}/role">
        <xsl:if test="text()">
          <skos:prefLabel>
            <xsl:value-of select="."/>
          </skos:prefLabel>
        </xsl:if>
        <org:roleProperty>
          <xsl:attribute name="rdf:resource">
            <xsl:text>http://www.w3.org/ns/org#</xsl:text>
            <xsl:choose>
              <xsl:when test="../../field[@name='Manager']/boolean/text()='true'">headOf</xsl:when>
              <xsl:otherwise>memberOf</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </org:roleProperty>
      </org:Role>
    </org:role>
  </xsl:template>

  <xsl:template match="field[@name='Person']/user" mode="in-post">
    <org:heldBy rdf:resource="{ex:agent-uri(.)}"/>
  </xsl:template>

  <xsl:template match="field[@name='Team']/lookup" mode="in-post">
    <org:postIn rdf:resource="{ex:team-uri(key('teams', @id))}"/>
  </xsl:template>

  <xsl:template match="field[@name='Assists']/lookup" mode="in-post">
    <xsl:if test="$internal">
      <adhoc:assistantTo rdf:resource="{ex:post-uri(key('staff', @id))}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Office']/text[text()]" mode="in-post">
    <xsl:if test="$internal">
      <xsl:variable name="building-uri">
        <xsl:text>http://oxpoints.oucs.ox.ac.uk/id/</xsl:text>
        <xsl:choose>
          <xsl:when test="text()='Banbury Road'">40002001</xsl:when>
          <xsl:when test="text()='Blue Boar Court'">23233619</xsl:when>
          <xsl:when test="text()='Hythe Bridge Street'">23233672</xsl:when>
          <xsl:when test="text()='Malthouse'">23233636</xsl:when>
          <xsl:when test="text()='Parks Road'">23233753</xsl:when>
          <xsl:when test="text()='Wellington Square'">23233665</xsl:when>
          <xsl:when test="text()='Worcester Street'">23233614</xsl:when>
          <xsl:when test="text()='Gibson'">55329098</xsl:when>
          <xsl:when test="text()='Dartington House'">23233683</xsl:when>
        </xsl:choose>
      </xsl:variable>
      <xsl:variable name="space" select="normalize-space(../../field[@name='Space']/text/text())"/>
      <org:basedAt rdf:resource="{$building-uri}"/>
      <adhoc:building rdf:resource="{$building-uri}"/>
      <xsl:if test="$space">
        <adhoc:space>
          <geo:SpatialThing rdf:about="https://data.ox.ac.uk/id/estates/{$space}">
            <humfrey:noIndex rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</humfrey:noIndex>
            <rdfs:label>
              <xsl:value-of select="$space"/>
            </rdfs:label>
            <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/estates">
              <xsl:value-of select="$space"/>
            </skos:notation>
            <spatialrelations:within rdf:resource="{$building-uri}"/>
          </geo:SpatialThing>
        </adhoc:space>
      </xsl:if>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="field[@name='Manager0']/lookup[@id]" mode="in-post">
    <xsl:if test="$internal">
      <org:reportsTo rdf:resource="{ex:post-uri(key('staff', @id))}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="row" mode="infer-manager">
    <xsl:if test="$internal">
      <xsl:variable name="team" select="key('teams', fields/field[@name='Team']/lookup/@id)"/>
      <xsl:variable name="team-of-manager">
        <xsl:choose>
          <xsl:when test="fields/field[@name='Manager']/boolean/text()='true'">
            <xsl:if test="$team/fields/field[@name='Part_x0020_of']/lookup/@id">
              <xsl:value-of select="key('teams', $team/fields/field[@name='Part_x0020_of']/lookup/@id)/@id"/>
            </xsl:if>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$team/@id"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <xsl:if test="$team-of-manager">
        <xsl:variable name="managers" select="key('team-managers', $team-of-manager)"/>
        <xsl:for-each select="$managers">
          <org:reportsTo rdf:resource="{ex:post-uri(.)}"/>
        </xsl:for-each>
      </xsl:if>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
