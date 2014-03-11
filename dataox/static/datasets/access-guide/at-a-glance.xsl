<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:access="http://purl.org/net/accessiblity/"
    xmlns:parkingType="http://purl.org/net/accessiblity/parkingType"
    xmlns:doorEntryType="http://purl.org/net/accessiblity/doorEntryType"
    xmlns:humfrey="http://purl.org/NET/humfrey/ns/"
    version="2.0">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates select="/xml/building"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="building">
    <rdf:Description rdf:about="https://data.ox.ac.uk/id/access-guide-entry/{position()}">
      <xsl:apply-templates select="*|@*"/>
    </rdf:Description>
  </xsl:template>

  <xsl:template match="@oxpointsid">
    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/oxpoints">
      <xsl:value-of select="."/>
    </skos:notation>
  </xsl:template>

  <xsl:template match="parking|parkinng">
    <xsl:variable name="term">
      <xsl:choose>
        <xsl:when test="text()='Blue Badge'">BlueBadge</xsl:when>
        <xsl:when test="text()='Pay and Display'">PayAndDisplay</xsl:when>
        <xsl:otherwise>
          <xsl:message>Unexpected parking type: <xsl:value-of select="text()"/></xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$term">
      <access:nearbyParkingType rdf:resource="http://purl.org/net/accessiblity/parkingType/{$term}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="entrance">
    <access:mainEntranceHasLevelAccess rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">
      <xsl:choose>
        <xsl:when test="text()='Level'">true</xsl:when>
        <xsl:otherwise>false</xsl:otherwise>
      </xsl:choose>
    </access:mainEntranceHasLevelAccess>
  </xsl:template>

  <xsl:template match="altentrance">
    <access:hasLevelAccess rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">
      <xsl:choose>
        <xsl:when test="text()='1'">true</xsl:when>
        <xsl:otherwise>false</xsl:otherwise>
      </xsl:choose>
    </access:hasLevelAccess>
  </xsl:template>

  <xsl:template match="doorentry">
    <xsl:variable name="term">
      <xsl:choose>
        <xsl:when test="text()='Manual'">Manual</xsl:when>
        <xsl:when test="text()='Powered'">Powered</xsl:when>
        <xsl:when test="text()='Automatic'">Automatic</xsl:when>
        <xsl:otherwise>
          <xsl:message>Unexpected door entry type: <xsl:value-of select="text()"/></xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$term">
      <access:doorEntryType rdf:resource="http://purl.org/net/accessiblity/doorEntryType/{$term}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="floors">
    <access:numberOfFloors rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">
      <xsl:value-of select="."/>
    </access:numberOfFloors>
  </xsl:template>

  <xsl:template match="accesstoilets">
    <access:numberOfAccessibleToilets rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">
      <xsl:value-of select="."/>
    </access:numberOfAccessibleToilets>
  </xsl:template>

  <xsl:template match="@*|node()"/>
</xsl:stylesheet>
  
