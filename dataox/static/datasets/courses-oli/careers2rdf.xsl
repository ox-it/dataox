<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >
  <xsl:import href="../courses/spreadsheet2rdf.xsl"/>

  <xsl:variable name="base">https://course.data.ox.ac.uk/id/oli/</xsl:variable>
  <xsl:variable name="publisher">http://oxpoints.oucs.ox.ac.uk/id/23232618</xsl:variable>
  <xsl:variable name="publisher-name">the Oxford Learning Institute</xsl:variable>
  <xsl:variable name="course-notation">https://data.ox.ac.uk/id/notation/oli-course</xsl:variable>
  <xsl:variable name="presentation-notation">https://data.ox.ac.uk/id/notation/oli-presentation</xsl:variable>
  <xsl:variable name="slugify-fields" select="('course-identifier')"/>
</xsl:stylesheet>
