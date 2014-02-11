<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    version="2.0">

  <xsl:template name="telephone-extension">
    <!-- Last five characters. Remember strings are 1-indexed, not 0-indexed. -->
    <xsl:variable name="digits" select="replace(., '[^0-9]', '')"/>
    <xsl:variable name="extension" select="substring($digits, string-length($digits)-4)"/>
    <xsl:variable name="prefix">
      <!-- From page 6 of the Internal Telephone Directory ("Extensions") -->
      <xsl:choose>
        <xsl:when test="starts-with($extension, '1')">6</xsl:when>
        <xsl:when test="starts-with($extension, '7')">2</xsl:when>
        <xsl:when test="starts-with($extension, '8')">2</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$prefix">
      <v:tel>
        <v:Voice rdf:about="tel:+441865{$prefix}{$extension}">
          <rdfs:label>01865 (<xsl:value-of select="$prefix"/>)<xsl:value-of select="$extension"/></rdfs:label>
        </v:Voice>
      </v:tel>
    </xsl:if>
    <adhoc:oxfordExtensionNumber>
      <xsl:value-of select="$extension"/>
    </adhoc:oxfordExtensionNumber>
  </xsl:template>
</xsl:stylesheet>
