<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oxcap="http://purl.ox.ac.uk/oxcap/ns/">
  <xsl:import href="https://raw.github.com/ox-it/xcri-rdf/master/stylesheets/xcri2rdf.xsl"/>

  <xsl:template match="oxcap:bookingEndpoint">
    <oxcap:bookingEndpoint rdf:resource="{text()}"/>
  </xsl:template>
  
  <xsl:template match="@oxcap:visibility">
    <xsl:variable name="mapped">
      <xsl:choose>
        <xsl:when test=".='AC'">active</xsl:when>
        <xsl:when test=".='DC'">discontinued</xsl:when>
        <xsl:when test=".='CN'">cancelled</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <oxcap:status rdf:resource="http://purl.ox.ac.uk/oxcap/ns/status-{$mapped}"/>
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


</xsl:stylesheet>
