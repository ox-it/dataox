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
  <xsl:import href="../common/sharepoint.xsl"/>
  <xsl:import href="../common/telephone.xsl"/>
  <xsl:import href="../common/slugify.xsl"/>

  <xsl:variable name="base-uri">https://id.it.ox.ac.uk/</xsl:variable>
  <xsl:variable name="team-base-uri">https://id.it.ox.ac.uk/team/</xsl:variable>
  <xsl:variable name="service-category-base-uri">https://id.it.ox.ac.uk/service-category</xsl:variable>
  <xsl:variable name="it-services">http://oxpoints.oucs.ox.ac.uk/id/31337175</xsl:variable>
  <xsl:variable name="university-of-oxford">http://oxpoints.oucs.ox.ac.uk/id/00000000</xsl:variable>
  <xsl:variable name="group-base-uri">https://data.ox.ac.uk/id/group/unit-member/</xsl:variable>
  <xsl:variable name="service-classification-base-uri">http://id.ja.net/xray-service-classification</xsl:variable>

  <xsl:key name="teams" match="/site/lists/list[@name='Teams']/rows/row" use="@id"/>
  <xsl:key name="services" match="/site/lists/list[@name='Service Catalogue']/rows/row" use="@id"/>
  <xsl:key name="services-by-slug" match="/site/lists/list[@name='Service Catalogue']/rows/row" use="fields/field[@name='Slug']/text/text()"/>
  <xsl:key name="service-classifications" match="/site/lists/list[@name='Service classifications']/rows/row" use="@id"/>

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

  <xsl:function name="ex:service-uri">
    <xsl:param name="type"/>
    <xsl:param name="service"/>
    <xsl:choose>
      <xsl:when test="$type='service' and $service/fields/field[@name='URI']/text/text()">
        <xsl:value-of select="$service/fields/field[@name='URI']/text/text()"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$base-uri"/>
        <xsl:value-of select="$type"/>
        <xsl:text>/</xsl:text>
        <xsl:choose>
          <xsl:when test="$service//field[@name='Slug']/text/text()">
            <xsl:value-of select="$service//field[@name='Slug']/text/text()"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$service/@id"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <xsl:function name="ex:service-classification-uri">
    <xsl:param name="service-classification"/>
    <xsl:for-each select="$service-classification">
      <xsl:value-of select="concat($service-classification-base-uri, '/', key('service-classifications', @id)/fields/field[@name='Slug']/text/text())"/>
    </xsl:for-each>
  </xsl:function>
</xsl:stylesheet>
