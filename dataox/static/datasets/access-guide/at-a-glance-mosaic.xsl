<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:lyou="http://purl.org/linkingyou/"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    version="2.0">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates select="/items/item"/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="item[string-length(listing_details/tertiary_text/text()) gt 0]">
    <rdf:Description rdf:about="http://oxpoints.oucs.ox.ac.uk/id/{listing_details/tertiary_text}">
      <xsl:apply-templates select="*|@*"/>
    </rdf:Description>
  </xsl:template>

  <xsl:template match="@node_id">
    <lyou:space-accessibility rdf:resource="https://accessguide.web.ox.ac.uk/node/{.}"/>
  </xsl:template>

  <xsl:template match="listing_details/image_url">
    <xsl:if test="string-length(text()) gt 25">
      <adhoc:accessGuideImage rdf:resource="{text()}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="@*|node()" mode="#all">
    <xsl:apply-templates select="*" mode="#current"/>
  </xsl:template>
</xsl:stylesheet>
