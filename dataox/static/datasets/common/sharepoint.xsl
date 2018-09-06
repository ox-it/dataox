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

  <xsl:variable name="person-base-uri">https://data.ox.ac.uk/id/person/</xsl:variable>
  <xsl:variable name="group-base-uri">https://data.ox.ac.uk/id/group/unit-member/</xsl:variable>

  <xsl:key name="users" match="/site/lists/list[@name='User Information List']/rows/row" use="@id"/>

  <xsl:function name="ex:agent-uri">
    <xsl:param name="element"/>
    <xsl:for-each select="$element">
      <xsl:variable name="user" select="key('users', @id)"/>
      <xsl:choose>
        <xsl:when test="not($user)">
          <xsl:message>
            InVaLiD user <xsl:value-of select="@id"/> on row <xsl:value-of select="../../../@id"/> of list "<xsl:value-of select="../../../../../@name"/>"
            Whole row:
            <xsl:value-of select="../../.."/>
            <xsl:value-of select="$user"/>
          </xsl:message>
          <xsl:value-of select="concat($group-base-uri, @id)"/>
        </xsl:when>
        <xsl:when test="$user//field[@name='ContentType']/text='DomainGroup'">
          <xsl:value-of select="$group-base-uri"/>
          <xsl:value-of select="substring-after($user//field[@name='Name']/text, 'AD-OAK\group_')"/>
        </xsl:when>
        <xsl:when test="$user//field[@name='ContentType']/text='Person'">
          <xsl:value-of select="$person-base-uri"/>
          <xsl:value-of select="$user//field[@name='UserName']/text/text()"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:message terminate="yes">Unexpected ContentType: "<xsl:value-of select="$user//field[@name='ContentType']/text"/>" on user <xsl:value-of select="@id"/>; terminating.</xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:function>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates/>
    </rdf:RDF>
  </xsl:template>

  <!-- Don't serialize rows unless more explicitly matched -->
  <xsl:template match="list/rows/row"/>

  <xsl:template match="*" mode="#all">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  <xsl:template match="text()|@*" mode="#all"/>
</xsl:stylesheet>
