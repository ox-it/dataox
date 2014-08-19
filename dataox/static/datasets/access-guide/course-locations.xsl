<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    version="2.0">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates select="//table[head/text()='Locations']/row[position() gt 1 and cell[11]/text()='Y']"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="row">
    <xsl:variable name="row" select="."/>
    <xsl:for-each select="cell[4 lt position() and position() lt 10 and text()]">
      <rdf:Description>
        <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/estates">
          <xsl:value-of select="text()"/>
        </skos:notation>
        <adhoc:firstYearTeachingForCourseWithTitle>
          <xsl:value-of select="../cell[3]/text()"/>
        </adhoc:firstYearTeachingForCourseWithTitle>
      </rdf:Description>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
