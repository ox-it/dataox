<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
  <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#">
  <!ENTITY xhtml "http://www.w3.org/1999/xhtml">
  <!ENTITY xtypes "http://purl.org/xtypes/">
]>
<xsl:stylesheet version="2.0"
    xmlns="http://xcri.org/profiles/1.2/catalog"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:xmlo="http://purl.org/net/mlo"
    xmlns:prog="http://purl.org/prog/"
    xmlns:event="http://purl.org/NET/c4dm/event.owl#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:tl="http://purl.org/NET/c4dm/timeline.owl#"
    xmlns:oxcap="http://purl.ox.ac.uk/oxcap/ns/">
  <xsl:import href="https://raw.github.com/ox-it/xcri-rdf/master/stylesheets/xcri2rdf.xsl"/>

  <xsl:template match="oxcap:bookingEndpoint">
    <oxcap:bookingEndpoint rdf:resource="{text()}"/>
  </xsl:template>

  <xsl:template match="@oxcap:status">
    <xsl:variable name="mapped">
      <xsl:choose>
        <xsl:when test=".='AC'">active</xsl:when>
        <xsl:when test=".='DC'">discontinued</xsl:when>
        <xsl:when test=".='CN'">cancelled</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <oxcap:status rdf:resource="http://purl.ox.ac.uk/oxcap/ns/status-{$mapped}"/>
  </xsl:template>

  <xsl:template match="@oxcap:visibility">
    <xsl:variable name="mapped">
      <xsl:choose>
        <xsl:when test=".='PB'">public</xsl:when>
        <xsl:when test=".='RS'">restricted</xsl:when>
        <xsl:when test=".='PR'">private</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <oxcap:visibility rdf:resource="http://purl.ox.ac.uk/oxcap/ns/visibility-{$mapped}"/>
  </xsl:template>

  <xsl:template match="course">
    <xsl:if test="regulations/@oxcap:eligibility">
      <xsl:variable name="mapped">
        <xsl:choose>
          <xsl:when test="regulations/@oxcap:eligibility='OX'">members</xsl:when>
          <xsl:when test="regulations/@oxcap:eligibility='ST'">staff</xsl:when>
          <xsl:when test="regulations/@oxcap:eligibility='PU'">public</xsl:when>
        </xsl:choose>
      </xsl:variable>
      <oxcap:eligibility rdf:resource="http://purl.ox.ac.uk/oxcap/ns/eligibility-{$mapped}"/>
    </xsl:if>
    <xsl:apply-imports/>
  </xsl:template>

  <xsl:template match="oxcap:session">
    <oxcap:consistsOf>
      <oxcap:Session>
        <xsl:apply-templates select="." mode="rdf-about-attribute"/>
        <xsl:apply-templates select="@*|*"/>
      </oxcap:Session>
    </oxcap:consistsOf>
  </xsl:template>

  <xsl:template match="oxcap:session" mode="rdf-about">
    <xsl:variable name="identifier" select="dc:identifier[not(@xsi:type) and (starts-with(text(), 'http:') or starts-with(text(), 'https:'))]"/>
    <xsl:choose>
      <xsl:when test="$identifier">
        <xsl:value-of select="$identifier[1]/text()"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select=".." mode="rdf-about"/>
        <xsl:text>/session/</xsl:text>
        <xsl:value-of select="count(preceding-sibling::oxcap:session)+1"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
