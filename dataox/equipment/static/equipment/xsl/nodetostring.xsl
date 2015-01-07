<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!--
	Converts a nodeset to string, especially useful for json conversions.

	===================================================================================

	Copyright 2011, Thomas Appel, http://thomas-appel.com, mail(at)thomas-appel.com
	dual licensed under MIT and GPL license
	http://dev.thomas-appel.com/licenses/mit.txt
	http://dev.thomas-appel.com/licenses/gpl.txt

	===================================================================================

	Example usage:

	(convert a exsl nodeset to string: )
	___

	<xsl:variable name="somelink">
		<a href="{url}" class="some-class"><xsl:value-of select="name"/></a>
	</xsl:variable>
	<xsl:apply-templates select="exsl:node-set($somelink)/* | exsl:node-set($some-link)/text()"/>
	___

	(convert xml noset to string: )
	___

	<xsl:apply-templates select="node | node[text()]"/>

-->
	<xsl:variable name="q">
		<xsl:text>"</xsl:text>
	</xsl:variable>
	<xsl:variable name="empty"/>


	<xsl:template match="*" mode="selfclosetag">
	        <xsl:param name="namespaces-in-scope"/>
		<xsl:text>&lt;</xsl:text>
		<xsl:value-of select="name()"/>
		<xsl:apply-templates select="." mode="namespaces">
		  <xsl:with-param name="namespaces-in-scope" select="$namespaces-in-scope"/>
		</xsl:apply-templates>
		<xsl:apply-templates select="@*" mode="attribs"/>
		<xsl:text>/&gt;</xsl:text>
	</xsl:template>

	<xsl:template match="*" mode="opentag">
	        <xsl:param name="namespaces-in-scope"/>
		<xsl:text>&lt;</xsl:text>
		<xsl:value-of select="name()"/>
		<xsl:apply-templates select="." mode="namespaces">
		  <xsl:with-param name="namespaces-in-scope" select="$namespaces-in-scope"/>
		</xsl:apply-templates>
		<xsl:apply-templates select="@*" mode="attribs"/>
		<xsl:text>&gt;</xsl:text>
	</xsl:template>

	<xsl:template match="*" mode="closetag">
		<xsl:text>&lt;/</xsl:text>
		<xsl:value-of select="name()"/>
		<xsl:text>&gt;</xsl:text>
	</xsl:template>

	<xsl:template match="*" mode="namespaces">
	        <xsl:param name="namespaces-in-scope"/>
		<xsl:if test="not(index-of($namespaces-in-scope, substring-before(name(), ':')))">
		    <xsl:text> xmlns:</xsl:text>
		    <xsl:value-of select="substring-before(name(), ':')"/>
		    <xsl:text>="</xsl:text>
		    <xsl:value-of select="namespace-uri()"/>
		    <xsl:text>"</xsl:text>
		</xsl:if>
	</xsl:template>

	<xsl:template match="* | text()" mode="nodetostring">
	        <xsl:param name="namespaces-in-scope"/>
		<xsl:choose>
			<xsl:when test="boolean(name())">
				<xsl:choose>
					<!--
						 if element is not empty
					-->
					<xsl:when test="normalize-space(.) != $empty or *">
						<xsl:apply-templates select="." mode="opentag">
							<xsl:with-param name="namespaces-in-scope" select="$namespaces-in-scope"/>
						</xsl:apply-templates>
						<xsl:apply-templates select="* | text()" mode="nodetostring">
							<xsl:with-param name="namespaces-in-scope" select="in-scope-prefixes(.)"/>
						</xsl:apply-templates>
						<xsl:apply-templates select="." mode="closetag"/>
					</xsl:when>
					<!--
						 assuming emty tags are self closing, e.g. <img/>, <source/>, <input/>
					-->
					<xsl:otherwise>
						<xsl:apply-templates select="." mode="selfclosetag">
							<xsl:with-param name="namespaces-in-scope" select="$namespaces-in-scope"/>
						</xsl:apply-templates>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="replace(replace(replace(., '&amp;', '&amp;amp;'), '&gt;', '&amp;gt;'), '&lt;', '&amp;lt;')"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="@*" mode="attribs">
		<xsl:value-of select="concat(' ', name(), '=', $q, ., $q)"/>
	</xsl:template>

</xsl:stylesheet>

