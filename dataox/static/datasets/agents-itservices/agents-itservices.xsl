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
  <xsl:output method="xml" indent="yes"/>

  <xsl:param name="store"/>
  <xsl:variable name="internal" select="$store='itservices'"/>

  <xsl:variable name="person-base-uri">https://data.ox.ac.uk/id/person/</xsl:variable>
  <xsl:variable name="team-base-uri">https://data.ox.ac.uk/id/itservices/team/</xsl:variable>
  <xsl:variable name="group-base-uri">https://data.ox.ac.uk/id/group/unit-member/</xsl:variable>

  <xsl:key name="users" match="/site/users/user" use="@id"/>
  <xsl:key name="teams" match="/site/lists/list[@name='Teams']/rows/row" use="@id"/>
  <xsl:key name="memberships" match="/site/lists/list[@name='Teams']/rows/row" use="fields/field[@name='Members']/user/@id"/>
  <xsl:key name="managerships" match="/site/lists/list[@name='Teams']/rows/row" use="fields/field[@name='Managers']/user/@id"/>

  <xsl:function name="ex:agent-uri">
    <xsl:param name="element"/>
    <xsl:for-each select="$element">
      <xsl:variable name="user" select="key('users', @id)"/>
      <xsl:choose>
        <xsl:when test="$user/d:ContentType='DomainGroup'">
          <xsl:value-of select="$group-base-uri"/>
          <xsl:value-of select="substring-after($user/d:Account, 'AD-OAK\group_')"/>
        </xsl:when>
        <xsl:when test="$user/d:ContentType='Person'">
          <xsl:value-of select="$person-base-uri"/>
          <xsl:value-of select="$user/d:UserName"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:message terminate="yes">Unexpected d:ContentType: "<xsl:value-of select="$user/d:ContentType"/>" on user <xsl:value-of select="@id"/>; terminating.</xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:function>

  <xsl:function name="ex:team-uri">
    <xsl:param name="team"/>
    <xsl:choose>
      <xsl:when test="$team/fields/field[@name='URI']/text/text()">
        <xsl:value-of select="$team/fields/field[@name='URI']/text/text()"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$team-base-uri"/>
        <xsl:value-of select="$team/@id"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="*" mode="#all">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  <xsl:template match="text()|@*" mode="#all"/>

  <xsl:template match="list[@name='Teams']/rows/row">
    <xsl:if test="$internal and not(fields/field[@name='URI']/text/text())">
      <org:OrganizationalUnit rdf:about="{ex:team-uri(.)}">
        <xsl:apply-templates mode="in-team"/>
      </org:OrganizationalUnit>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]" mode="in-team">
    <rdfs:label>
      <xsl:value-of select="."/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="field[@name='Part_x0020_of']/lookup" mode="in-team">
    <org:subOrganizationOf rdf:resource="{ex:team-uri(key('teams', @id))}"/>
  </xsl:template>

  <xsl:template match="users/user">
    <xsl:if test="$internal or d:ContentType = 'DomainGroup'">
      <xsl:element name="{if (d:ContentType = 'DomainGroup') then 'gr:BusinessEntityType' else 'foaf:Person'}">
        <xsl:attribute name="rdf:about">
          <xsl:value-of select="ex:agent-uri(.)"/>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="d:ContentType = 'DomainGroup'">
            <xsl:apply-templates select="*[not(@m:null='true')]" mode="in-domain-group"/>
          </xsl:when>
          <xsl:when test="d:ContentType = 'Person'">
            <xsl:apply-templates select="*[not(@m:null='true')]" mode="in-person"/>
            <xsl:for-each select="key('managerships', @id)">
              <org:headOf rdf:resource="{ex:team-uri(.)}"/>
            </xsl:for-each>
            <xsl:for-each select="key('memberships', @id)">
              <org:memberOf rdf:resource="{ex:team-uri(.)}"/>
            </xsl:for-each>
          </xsl:when>
        </xsl:choose>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <xsl:template match="d:Name" mode="in-domain-group">
    <rdfs:label>
      <xsl:value-of select="substring-before(., ' Group')"/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="d:Name" mode="in-person">
    <foaf:name>
      <xsl:value-of select="."/>
    </foaf:name>
  </xsl:template>

  <xsl:template match="d:FirstName" mode="in-person">
    <foaf:firstName>
      <xsl:value-of select="."/>
    </foaf:firstName>
  </xsl:template>

  <xsl:template match="d:LastName" mode="in-person">
    <foaf:lastName>
      <xsl:value-of select="."/>
    </foaf:lastName>
  </xsl:template>

  <xsl:template match="d:WorkEMail" mode="in-person">
    <foaf:mbox rdf:resource="mailto:{.}"/>
  </xsl:template>

  <xsl:template match="d:WorkPhone" mode="in-person">
    <xsl:variable name="phone" select="replace(., '[^\d]', '')"/>
    <v:tel>
      <v:Voice rdf:about="tel:+44{substring($phone, 2)}"/>
    </v:tel>
    <adhoc:oxfordExtensionNumber>
      <xsl:value-of select="substring($phone, 7)"/>
    </adhoc:oxfordExtensionNumber>
  </xsl:template>
</xsl:stylesheet>
