<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
  <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#">
  <!ENTITY xhtml "http://www.w3.org/1999/xhtml">
  <!ENTITY xtypes "http://purl.org/xtypes/">
]>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:xhtml="http://www.w3.org/1999/xhtml#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:event="http://purl.org/NET/c4dm/event.owl#"
    xmlns:prog="http://purl.org/prog/"
    xmlns:tl="http://purl.org/NET/c4dm/timeline.owl#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:mlo="http://purl.org/net/mlo/"
    xmlns:xmlo="http://purl.org/net/mlo"
    xmlns:xcri="http://xcri.org/profiles/1.2/"
    xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    xmlns:org="http://www.w3.org/ns/org#"
    xmlns:time="http://www.w3.org/2006/time#"
    xmlns:ex="http://www.example.org/"
    xmlns:humfrey="http://purl.org/NET/humfrey/ns/"
    xmlns:oxcap="http://purl.ox.ac.uk/oxcap/ns/"
    xmlns:tio="http://purl.org/tio/ns#"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
  <xsl:output method="xml" indent="yes"/>

  <xsl:param name="store">public</xsl:param>
  <xsl:param name="skip-first"/>
  <xsl:variable name="base"/>
  <xsl:variable name="publisher"/>
  <xsl:variable name="course-notation">https://data.ox.ac.uk/id/notation/daisy-course</xsl:variable>
  <xsl:variable name="presentation-notation">https://data.ox.ac.uk/id/notation/daisy-presentation</xsl:variable>

  <xsl:function name="ex:slugify">
    <xsl:param name="term"/>
    <xsl:choose>
      <xsl:when test="contains($term, '(')">
        <xsl:value-of select="ex:slugify(substring-before($term, '('))"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="replace(lower-case(normalize-space($term)), '[^a-z0-9]+', '-')"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <xsl:template match="/">
    <xsl:variable name="data">
      <courses>
        <xsl:choose>
          <xsl:when test="$skip-first">
            <xsl:apply-templates select="/tei:TEI/tei:text/tei:body/tei:table/tei:row[position() &gt; 1]" mode="preprocess"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="/tei:TEI/tei:text/tei:body/tei:table/tei:row" mode="preprocess"/>
          </xsl:otherwise>
        </xsl:choose>
      </courses>
    </xsl:variable>
    <rdf:RDF>
      <xcri:catalog rdf:about="{$base}catalogue">
        <rdfs:label>Courses from <xsl:value-of select="$publisher-name"/> at the University of Oxford</rdfs:label>
        <dcterms:publisher rdf:resource="{$publisher}"/>
        <xsl:for-each select="$data/courses/course">
          <skos:member rdf:resource="{$base}course/{course-identifier/text()}"/>
        </xsl:for-each>
      </xcri:catalog>
      <xsl:for-each-group select="$data/courses/course" group-by="provider-identifier">
        <xsl:apply-templates select="." mode="provider"/>
      </xsl:for-each-group>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="tei:row" mode="preprocess">
    <xsl:variable name="row" select="."/>
    <xsl:if test="tei:cell[7]/text()='PB' or ($store='courses' and tei:cell[7]/text()='RS')">
      <course>
        <xsl:for-each select="$columns/*">
          <xsl:variable name="position" select="position()"/>
          <xsl:variable name="cell" select="$row/tei:cell[position()=$position]"/>
          <xsl:if test="$cell/text()">
            <xsl:element name="{name()}">
              <xsl:value-of select="$cell/text()"/>
            </xsl:element>
          </xsl:if>
        </xsl:for-each>
      </course>
    </xsl:if>
  </xsl:template>

  <xsl:template match="course" mode="provider">
    <org:Organization rdf:about="https://course.data.ox.ac.uk/id/provider/{provider-identifier/text()}">
      <xsl:apply-templates mode="provider-metadata"/>
      <xsl:for-each-group select="current-group()" group-by="course-identifier">
        <xsl:apply-templates select="." mode="in-provider">
          <xsl:with-param name="current-group" select="current-group()"/>
        </xsl:apply-templates>
      </xsl:for-each-group>
    </org:Organization>
  </xsl:template>

  <xsl:template match="course" mode="in-provider">
    <xsl:param name="current-group"/>
    <mlo:offers>
      <xsl:apply-templates select="." mode="course">
        <xsl:with-param name="current-group" select="$current-group"/>
      </xsl:apply-templates>
    </mlo:offers>
    <!-- 
    <xsl:for-each-group select="current-group()" group-by="presentation-start">
      <xsl:variable name="presentation-uri" select="concat($base, 'presentation/', course-identifier/text(), '/', position())"/>
      <xsl:variable name="offering-uri" select="concat($presentation-uri, '/offering')"/>
      <gr:offers>
        <gr:Offering rdf:about="{$offering-uri}">
          <gr:includes>
            <tio:TicketPlaceholder rdf:about="{$presentation-uri}/access">
              <tio:accessTo rdf:resource="{$presentation-uri}"/>
            </tio:TicketPlaceholder>
          </gr:includes>
          <xsl:apply-templates select="." mode="in-offering">
            <xsl:with-param name="presentation-uri" select="$presentation-uri"/>
            <xsl:with-param name="offering-uri" select="$offering-uri"/>
          </xsl:apply-templates>
        </gr:Offering>
      </gr:offers>
    </xsl:for-each-group> -->
  </xsl:template>

  <xsl:template match="course" mode="course">
    <xsl:param name="current-group"/>
    <xcri:course rdf:about="{$base}course/{course-identifier/text()}">
      <xsl:apply-templates select="*[text()]" mode="in-course"/>
      <xsl:for-each-group select="$current-group" group-by="presentation-start">
        <xsl:apply-templates select="." mode="in-course">
          <xsl:with-param name="current-group" select="current-group()"/>
        </xsl:apply-templates>
      </xsl:for-each-group>
    </xcri:course>
  </xsl:template>
  
  <xsl:template match="course" mode="in-course">
    <xsl:param name="current-group"/>
    <xsl:if test="presentation-start/text()">
      <mlo:specifies>
        <xsl:apply-templates select="." mode="presentation">
          <xsl:with-param name="current-group" select="$current-group"/>
        </xsl:apply-templates>
      </mlo:specifies>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="course" mode="presentation">
    <xsl:param name="current-group"/>
    <xsl:variable name="presentation-uri" select="concat($base, 'presentation/', course-identifier/text(), '/', position())"/>
    <xcri:presentation rdf:about="{$presentation-uri}">
      <skos:notation rdf:datatype="{$presentation-notation}">
        <xsl:value-of select="concat(course-identifier/text(), '-', position())"/>
      </skos:notation>
      <xsl:apply-templates select="*[text()]" mode="in-presentation">
        <xsl:with-param name="presentation-uri" select="$presentation-uri"/>
      </xsl:apply-templates>
      <xsl:for-each select="$current-group[session-date or session-start]">
        <xsl:sort select="session-date"/>
        <xsl:sort select="session-start"/>
        <xsl:apply-templates select="." mode="in-presentation">
          <xsl:with-param name="session-uri" select="concat($presentation-uri, '/session/', position())"/>
        </xsl:apply-templates>
      </xsl:for-each>
    </xcri:presentation>
  </xsl:template>
  
  <xsl:template match="course" mode="in-presentation">
    <xsl:param name="session-uri"/>
    <xsl:if test="session-identifiier/text()">
      <oxcap:consistsOf>
        <xsl:apply-templates select="." mode="session">
          <xsl:with-param name="session-uri" select="$session-uri"/>
        </xsl:apply-templates>
      </oxcap:consistsOf>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="course" mode="session">
    <xsl:param name="session-uri"/>
    <oxcap:Session rdf:about="{$session-uri}">
      <xsl:apply-templates select="*[text()]" mode="in-session">
        <xsl:with-param name="session-uri" select="$session-uri"/>
      </xsl:apply-templates>
    </oxcap:Session>
  </xsl:template>
 
  <xsl:template match="provider-identifier" mode="provider-metadata">
    <xsl:apply-templates select="text()" mode="notation"/>
  </xsl:template>

  <xsl:template match="provider-title" mode="in-provider">
    <rdfs:label>
      <xsl:value-of select="."/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="provider-description" mode="in-provider">
    <rdfs:comment>
      <xsl:value-of select="."/>
    </rdfs:comment>
  </xsl:template>

  <xsl:template match="provider-url" mode="in-provider">
    <foaf:homepage rdf:resource="{normalize-space(.)}"/>
  </xsl:template>


  <xsl:template match="course-title" mode="in-course">
    <rdfs:label>
      <xsl:value-of select="text()"/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="course-identifier" mode="in-course">
    <skos:notation rdf:datatype="{$course-notation}">
      <xsl:value-of select="."/>
    </skos:notation>
  </xsl:template>

  <xsl:template match="course-visibility" mode="in-course">
    <oxcap:visibility>
      <xsl:attribute name="rdf:resource">
        <xsl:text>http://purl.ox.ac.uk/oxcap/ns/visibility-</xsl:text>
	    <xsl:choose>
	      <xsl:when test=".='PB'">public</xsl:when>
	      <xsl:when test=".='RS'">restricted</xsl:when>
	      <xsl:when test=".='PR'">private</xsl:when>
    	</xsl:choose>
      </xsl:attribute>
    </oxcap:visibility>
  </xsl:template>

  <xsl:template match="member-apply-to" mode="in-presentation">
    <oxcap:memberApplyTo rdf:resource="{.}"/>
  </xsl:template>

  <xsl:template match="public-apply-to" mode="in-presentation">
    <xcri:applyTo rdf:resource="{.}"/>
  </xsl:template>
  
  <xsl:template match="presentation-start|presentation-start-text" mode="in-presentation">
    <xsl:param name="presentation-uri"/>
    <xsl:if test="not(self::presentation-start-text and ../presentation-start)">
      <mlo:start>
        <xsl:call-template name="instant">
          <xsl:with-param name="uri" select="concat($presentation-uri, '/start')"/>
          <xsl:with-param name="value" select="../presentation-start"/>
          <xsl:with-param name="label" select="../presentation-start-text"/>
        </xsl:call-template>
      </mlo:start>
    </xsl:if>
  </xsl:template>

  <xsl:template match="presentation-venue|presentation-venue-text" mode="in-presentation">
    <xsl:param name="presentation-uri"/>
    <xsl:if test="not(self::presentation-venue-text and ../presentation-venue)">
      <xcri:venue>
        <geo:SpatialThing rdf:about="{$base}presentation-venue/{ex:slugify(if (../presentation-venue-text) then ../presentation-venue-text else ../presentation-venue)}">
          <xsl:if test="../presentation-venue-text">
            <rdfs:label>
              <xsl:value-of select="../presentation-venue-text"/>
            </rdfs:label>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="matches(../presentation-venue, '\d{8}')">
              <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/oxpoints">
                <xsl:value-of select="../presentation-venue"/>
              </skos:notation>
            </xsl:when>
            <xsl:when test="matches(../presentation-venue, '\d{3}')">
              <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/estates">
                <xsl:value-of select="../presentation-venue"/>
              </skos:notation>
            </xsl:when>
            <xsl:otherwise>
              <humfrey:searchNormalization rdf:parseType="Resource">
                <humfrey:searchType>spatial-thing</humfrey:searchType>
                <humfrey:searchQuery><xsl:value-of select="text()"/></humfrey:searchQuery>
              </humfrey:searchNormalization>
            </xsl:otherwise>
          </xsl:choose>
        </geo:SpatialThing>
      </xcri:venue>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="presentation-status" mode="in-course">
    <xsl:if test="not(../presentation-start/text() or ../presentation-start-text/text())">
      <xsl:variable name="mapped">
        <xsl:choose>
          <xsl:when test="text()='AC'">active</xsl:when>
          <xsl:when test="text()='DC'">discontinued</xsl:when>
          <xsl:when test="text()='CN'">cancelled</xsl:when>
        </xsl:choose>
      </xsl:variable>
      <oxcap:status rdf:resource="http://purl.ox.ac.uk/oxcap/ns/status-{$mapped}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="presentation-status" mode="in-presentation">
    <xsl:variable name="mapped">
      <xsl:choose>
        <xsl:when test="text()='AC'">active</xsl:when>
        <xsl:when test="text()='DC'">discontinued</xsl:when>
        <xsl:when test="text()='CN'">cancelled</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <oxcap:status rdf:resource="http://purl.ox.ac.uk/oxcap/ns/status-{$mapped}"/>
  </xsl:template>

  <xsl:template match="course-learning-outcome" mode="in-course">
    <xcri:learningOutcome><xsl:value-of select="text()"/></xcri:learningOutcome>
  </xsl:template>
  
  <xsl:template match="course-prerequisite" mode="in-course">
    <xcri:regulations>
      <xsl:choose>
        <xsl:when test=".='PU'">Course open to the public.</xsl:when>
        <xsl:when test=".='OX'">Course open to members of the University of Oxford.</xsl:when>
        <xsl:when test=".='ST'">Course open to staff of the University of Oxford.</xsl:when>
      </xsl:choose>
    </xcri:regulations>
    <oxcap:eligibility>
      <xsl:attribute name="rdf:resource">
        <xsl:text>http://purl.ox.ac.uk/oxcap/ns/eligibility-</xsl:text>
        <xsl:choose>
          <xsl:when test=".='PU'">public</xsl:when>
          <xsl:when test=".='OX'">members</xsl:when>
          <xsl:when test=".='ST'">staff</xsl:when>
        </xsl:choose>
      </xsl:attribute>
    </oxcap:eligibility>
  </xsl:template>

  <xsl:template match="course-prerequisite" mode="in-offering">
    <gr:eligibleCustomerTypes>
      <xsl:attribute name="rdf:resource">
        <xsl:text>https://data.ox.ac.uk/id/group/</xsl:text>
        <xsl:choose>
          <xsl:when test=".='PU'">everyone</xsl:when>
          <xsl:when test=".='OX'">member</xsl:when>
          <xsl:when test=".='ST'">staff</xsl:when>
        </xsl:choose>
      </xsl:attribute>
    </gr:eligibleCustomerTypes>
  </xsl:template>

  <xsl:template match="course-audience" mode="in-course">
    <!-- TODO: Where does this go? --> 
  </xsl:template>
  
  <xsl:template match="course-subject" mode="in-course">
    <xsl:for-each select="tokenize(text(), ' ')">
      <dcterms:subject rdf:resource="http://jacs.dataincubator.org/{lower-case(.)}"/>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="course-skill" mode="in-course">
    <xsl:for-each select="tokenize(text(), ' ')">
      <dcterms:subject rdf:resource="https://data.ox.ac.uk/id/ox-rdf/descriptor/{.}"/>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="course-research-methods" mode="in-course">
    <xsl:for-each select="tokenize(text(), ' ')">
      <dcterms:subject rdf:resource="https://data.ox.ac.uk/id/ox-rm/descriptor/{.}"/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="course-description" mode="in-course">
    <dcterms:description>
      <xsl:value-of select="text()"/>
    </dcterms:description>
  </xsl:template>
  
  <xsl:template match="course-url" mode="in-course">
    <foaf:page rdf:resource="{normalize-space(.)}"/>
    <xsl:if test="not(../public-apply-to/text())">
      <xcri:applyTo rdf:resource="{normalize-space(.)}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="presentation-apply-from|presentation-apply-from-text" mode="in-presentation">
    <xsl:param name="presentation-uri"/>
    <xsl:if test="not(self::presentation-apply-from-text and ../presentation-apply-from)">
      <xcri:applyFrom>
        <xsl:call-template name="instant">
          <xsl:with-param name="uri" select="concat($presentation-uri, '/apply-from')"/>
          <xsl:with-param name="value" select="../presentation-apply-from"/>
          <xsl:with-param name="label" select="../presentation-apply-from-text"/>
        </xsl:call-template>
      </xcri:applyFrom>
    </xsl:if>
  </xsl:template>

  <xsl:template match="presentation-apply-until|presentation-apply-until-text" mode="in-presentation">
    <xsl:param name="presentation-uri"/>
    <xsl:if test="not(self::presentation-apply-until-text and ../presentation-apply-until)">
      <xcri:applyUntil>
        <xsl:call-template name="instant">
          <xsl:with-param name="uri" select="concat($presentation-uri, '/apply-until')"/>
          <xsl:with-param name="value" select="../presentation-apply-until"/>
          <xsl:with-param name="label" select="../presentation-apply-until-text"/>
        </xsl:call-template>
      </xcri:applyUntil>
    </xsl:if>
  </xsl:template>

  <xsl:template match="presentation-attendance-mode" mode="in-presentation">
    <xcri:attendanceMode rdf:resource="http://xcri.org/profiles/catalog/1.2/attendanceMode/{.}"/>
  </xsl:template>

  <xsl:template match="presentation-attendance-pattern" mode="in-presentation">
    <xcri:attendancePattern rdf:resource="http://xcri.org/profiles/catalog/1.2/attendancePattern/{.}"/>
  </xsl:template>

  <xsl:template match="presentation-end" mode="in-presentation">
    <xsl:param name="presentation-uri"/>
    <xcri:end>
      <xsl:call-template name="instant">
        <xsl:with-param name="uri" select="concat($presentation-uri, '/end')"/>
        <xsl:with-param name="value" select="."/>
      </xsl:call-template>
    </xcri:end>
  </xsl:template>

  <xsl:template match="presentation-places" mode="in-presentation">
    <mlo:places rdf:datatype="&xsd;int">
      <xsl:value-of select="."/>
    </mlo:places>
  </xsl:template>

  <xsl:template match="session-date" mode="in-session">
    <dcterms:date rdf:datatype="&xsd;date">
      <xsl:value-of select="."/>
    </dcterms:date>
  </xsl:template>
  
  <xsl:template match="session-start|session-end" mode="in-session">
    <xsl:param name="session-uri"/>
    <xsl:element name="{if (self::session-start) then 'mlo:start' else 'xcri:end'}">
      <time:Instant>
        <xsl:attribute name="rdf:about">
          <xsl:value-of select="concat($session-uri, if (self::session-start) then '/start' else '/end')"/>
        </xsl:attribute>
        <time:inXSDDateTime rdf:datatype="&xsd;dateTime">
          <xsl:value-of select="../session-start"/>
        </time:inXSDDateTime>
      </time:Instant>
    </xsl:element>
  </xsl:template>

  <xsl:template match="*" mode="#all"/>

  <xsl:template match="text()" mode="notation">
    <skos:notation>
      <xsl:attribute name="rdf:datatype">
        <xsl:text>https://data.ox.ac.uk/id/notation/</xsl:text>
        <xsl:choose>
          <xsl:when test="matches(., '^[A-Z][A-Z\d]$')">twoThree</xsl:when>
          <xsl:when test="matches(., '^\d{8}$')">oxpoints</xsl:when>
          <xsl:when test="matches(., '^\d[A-Z]$')">division</xsl:when>
		  <xsl:when test="matches(., '^\d[A-Z][A-Z\d]\d$')">department</xsl:when>
		  <xsl:when test="matches(., '^\d{3}$')">estates</xsl:when>
        </xsl:choose>
      </xsl:attribute>
      <xsl:value-of select="."/>
    </skos:notation>
  </xsl:template>

  <xsl:template name="instant">
    <xsl:param name="uri"/>
    <xsl:param name="value"/>
    <xsl:param name="label"/>
    
    <time:Instant rdf:about="{$uri}">
      <xsl:if test="$value">
        <xsl:element name="{if (string-length($value) &gt; 10) then 'xsd:inXSDDateTime' else 'rdf:value'}">
          <xsl:attribute name="rdf:datatype">
            <xsl:text>&xsd;</xsl:text>
            <xsl:choose>
              <xsl:when test="string-length($value) &gt; 10">dateTime</xsl:when>
              <xsl:when test="string-length($value) = 10">date</xsl:when>
              <xsl:when test="string-length($value) = 7">gYearMonth</xsl:when>
              <xsl:when test="string-length($value) = 4">gYear</xsl:when>
              <xsl:otherwise>string</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <xsl:value-of select="$value"/>
        </xsl:element>
      </xsl:if>
      <xsl:if test="$label">
        <rdfs:label><xsl:value-of select="$label"/></rdfs:label>
      </xsl:if>
    </time:Instant>
  </xsl:template>

  <xsl:variable name="columns">
    <!-- A-E -->
    <provider-identifier/>
    <provider-title/>
    <provider-description/>
    <provider-url/>
    <course-title/>
    <!-- F-J -->
    <course-identifier/>
    <course-visibility/>
    <member-apply-to/>
    <public-apply-to/>
    <presentation-start/>
    <!-- K-0 -->
    <presentation-start-text/>
    <presentation-venue/>
    <presentation-venue-text/>
    <presentation-status/>
    <course-learning-outcome/>
    <!-- P-T -->
    <course-prerequisite/>
    <course-audience/>
    <course-subject/>
    <course-skill/>
    <course-research-methods/>
    <!-- U-Y -->
    <course-description/>
    <course-url/>
    <presentation-apply-from/>
    <presentation-apply-from-text/>
    <presentation-apply-until/>
    <!-- Z-AD -->
    <presentation-apply-until-text/>
    <presentation-attendance-mode/>
    <presentation-attendance-pattern/>
    <presentation-end/>
    <presentation-places/>
    <!-- AE-AI -->
    <session-identififer/>
    <session-date/>
    <session-start/>
    <session-end/>
    <session-venue/>
    <!-- AJ-AN -->
    <session-venue-text/>
    <qualifications/>
  </xsl:variable>
</xsl:stylesheet>
