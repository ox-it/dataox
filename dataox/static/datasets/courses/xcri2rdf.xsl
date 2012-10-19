<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oxcap="http://purl.ox.ac.uk/oxcap/ns/">
  <xsl:import href="https://github.com/ox-it/xcri-rdf/blob/master/stylesheets/xcri2rdf.xsl"/>

  <xsl:template match="oxcap:bookingEndpoint">
    <oxcap:bookingEndpoint rdf:resource="{text()}"/>
  </xsl:template>
</xsl:stylesheet>
