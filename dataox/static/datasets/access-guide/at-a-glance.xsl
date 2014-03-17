<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:lyou="http://purl.org/linkingyou/"
    xmlns:access="http://purl.org/net/accessibility/"
    xmlns:parkingType="http://purl.org/net/accessibility/parkingType"
    xmlns:doorEntryType="http://purl.org/net/accessibility/doorEntryType"
    xmlns:humfrey="http://purl.org/NET/humfrey/ns/"
    xmlns:dataox="https://ox-it.github.io/dataox/ns/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    xmlns:oo="http://purl.org/openorg/"
    version="2.0">

  <xsl:import href="../common/telephone.xsl"/>
  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates select="/xml/building"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="building[string-length(@oxpointsid) gt 0]">
    <rdf:Description rdf:about="http://oxpoints.oucs.ox.ac.uk/id/{@oxpointsid}">
      <xsl:apply-templates select="*|@*"/>
    </rdf:Description>
  </xsl:template>

<!--
  <xsl:template match="@oxpointsid">
    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/oxpoints">
      <xsl:value-of select="."/>
    </skos:notation>
  </xsl:template>
-->

  <xsl:template match="url">
    <lyou:space-accessibility rdf:resource="{text()}"/>
  </xsl:template>

  <xsl:template match="buildingimage">
    <xsl:if test="string-length(text()) gt 25">
      <adhoc:accessGuideImage rdf:resource="{text()}"/>
    </xsl:if>
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
      <access:nearbyParkingType rdf:resource="http://purl.org/net/accessibility/parkingType/{$term}"/>
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
        <xsl:when test="text()='Check'">true</xsl:when>
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
      <access:doorEntryType rdf:resource="http://purl.org/net/accessibility/doorEntryType/{$term}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="floors">
    <access:numberOfFloors rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">
      <xsl:value-of select="."/>
    </access:numberOfFloors>
  </xsl:template>

  <xsl:template match="liftsallfloors">
    <xsl:copy-of select="dataox:yes-no-bool('access:liftsToAllFloors', .)"/>
  </xsl:template>
  <xsl:template match="hearingsystem">
    <xsl:copy-of select="dataox:yes-no-bool('access:hasHearingSystem', .)"/>
  </xsl:template>
  <xsl:template match="quietspace">
    <xsl:copy-of select="dataox:yes-no-bool('access:hasQuietSpace', .)"/>
  </xsl:template>
  <xsl:template match="caferefreshments">
    <xsl:copy-of select="dataox:yes-no-bool('access:hasCafeRefreshments', .)"/>
  </xsl:template>
  <xsl:template match="adaptedfurniture">
    <xsl:copy-of select="dataox:yes-no-bool('access:hasAdaptedFurniture', .)"/>
  </xsl:template>
  <xsl:template match="computeraccess">
    <xsl:copy-of select="dataox:yes-no-bool('access:hasComputerAccess', .)"/>
  </xsl:template>

  <xsl:template match="accesstoilets">
    <access:numberOfAccessibleToilets rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">
      <xsl:value-of select="."/>
    </access:numberOfAccessibleToilets>
  </xsl:template>

  <xsl:template match="floorplan">
    <access:floorplan>
      <foaf:Document rdf:about="{url/text()}">
        <rdfs:label>
          <xsl:value-of select="description"/>
        </rdfs:label>
      </foaf:Document>
    </access:floorplan>
  </xsl:template>

  <xsl:template match="hours/termtime">
    <adhoc:openingHoursTermTime>
      <xsl:value-of select="text()"/>
    </adhoc:openingHoursTermTime>
  </xsl:template>

  <xsl:template match="hours/vacation">
    <adhoc:openingHoursVacation>
      <xsl:value-of select="text()"/>
    </adhoc:openingHoursVacation>
  </xsl:template>

  <xsl:template match="hours/closed">
    <adhoc:openingHoursClosed>
      <xsl:value-of select="text()"/>
    </adhoc:openingHoursClosed>
  </xsl:template>

  <xsl:template match="addresses/address[@category='access_enquiries']">
    <access:contact>
      <foaf:Agent rdf:about="http://oxpoints.oucs.ox.ac.uk/id/{../../@oxpointsid}/access-contact">
        <xsl:apply-templates/>
      </foaf:Agent>
    </access:contact>
  </xsl:template>

  <xsl:template match="addresses/address[@category='general']">
    <oo:contact>
      <foaf:Agent rdf:about="http://oxpoints.oucs.ox.ac.uk/id/{../../@oxpointsid}/contact">
        <xsl:apply-templates/>
      </foaf:Agent>
    </oo:contact>
  </xsl:template>

  <xsl:template match="contact_name">
    <rdfs:label>
      <xsl:value-of select="text()"/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="contact_email">
    <v:email rdf:resource="mailto:{text()}"/>
  </xsl:template>

  <xsl:template match="contact_tel">
    <xsl:call-template name="telephone-extension"/>
  </xsl:template>

  <xsl:function name="dataox:yes-no-bool">
    <xsl:param name="name"/>
    <xsl:param name="node"/>
    <xsl:variable name="value">
      <xsl:choose>
        <xsl:when test="$node/text()='No'">false</xsl:when>
        <xsl:when test="$node/text()='Yes'">true</xsl:when>
        <xsl:otherwise>
          <xsl:message>Unexpected bool value: <xsl:value-of select="$node/text()"/></xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$value">
      <xsl:element name="{$name}">
        <xsl:attribute name="rdf:datatype">http://www.w3.org/2001/XMLSchema#boolean</xsl:attribute>
        <xsl:value-of select="$value"/>
      </xsl:element>
    </xsl:if>
  </xsl:function>

  <xsl:template match="@*|node()">
    <xsl:apply-templates select="*"/>
  </xsl:template>
</xsl:stylesheet>
  
