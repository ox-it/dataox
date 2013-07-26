<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://xcri.org/profiles/1.2/catalog" xmlns:xcriTerms="http://xcri.org/profiles/catalog/terms" xmlns:xcri="http://xcri.org/profiles/1.2/catalog" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:oxcap="http://purl.ox.ac.uk/oxcap/ns/" xmlns:credit="http://purl.org/net/cm" xmlns:mlo="http://purl.org/net/mlo" xmlns:courseDataProgramme="http://xcri.co.uk" xmlns:oxnotation="https://data.ox.ac.uk/id/notation/" xmlns:ox-rm="https://data.ox.ac.uk/id/ox-rm/" xmlns:ox-rdf="https://data.ox.ac.uk/id/ox-rdf/" xmlns:sharepoint="https://github.com/ox-it/python-sharepoint/" xpath-default-namespace="http://schemas.microsoft.com/office/infopath/2003/myXSD/2012-03-17T23:37:18" version="2.0">
  <xsl:output indent="yes"/>

  <xsl:template match="/">
    <catalog xsi:schemaLocation="http://xcri.org/profiles/1.2/catalog http://www.xcri.co.uk/bindings/xcri_cap_1_2.xsd http://xcri.org/profiles/1.2/catalog/terms  http://www.xcri.co.uk/bindings/xcri_cap_terms_1_2.xsd http://xcri.co.uk http://www.xcri.co.uk/bindings/coursedataprogramme.xsd" generated="{current-dateTime()}">
      <dc:title>Course data stored in SharePoint</dc:title>
      <dc:provider>
        <dc:identifier xsi:type="oxnotation:oxpoints">31337175</dc:identifier>
      </dc:provider>
      <dc:identifier>https://course.data.ox.ac.uk/id/sharepoint/catalogue</dc:identifier>
      <dc:description>from SP InfoPath docs</dc:description>
      <xsl:for-each-group select=".//myFields" group-by="normalize-space(upper-case(txt_identifier))">
        <provider>
          <xsl:apply-templates select="current-group()[1]/*" mode="provider"/>
          <xsl:for-each-group select="current-group()" group-by="normalize-space(upper-case(txt_cidentifier))">
            <course>
              <xsl:apply-templates select="current-group()[1]/*" mode="course-attribute"/>
              <!-- all are graduate training -->
              <dc:subject xsi:type="ox-rdf:notation" identifier="GT">Graduate Training</dc:subject>
              <xsl:apply-templates select="current-group()[1]/*" mode="course"/>
              <xsl:for-each select="current-group()">
                <presentation>
                  <xsl:apply-templates select="*" mode="presentation-attribute"/>
                  <xsl:apply-templates select="*" mode="presentation"/>
                </presentation>
              </xsl:for-each>
            </course>
          </xsl:for-each-group>
        </provider>
      </xsl:for-each-group>
    </catalog>
  </xsl:template>

  <!-- Provider identifier -->
  <xsl:template match="txt_identifier" mode="provider">
    <xsl:variable name="provider-identifier" select="normalize-space(upper-case(.))"/>
    <dc:identifier>
      <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/provider/</xsl:text>
      <xsl:value-of select="$provider-identifier"/>
    </dc:identifier>
    <xsl:choose>
      <xsl:when test="string-length($provider-identifier) = 2">
        <dc:identifier xsi:type="oxnotation:twoThree">
          <xsl:value-of select="upper-case($provider-identifier)"/>
        </dc:identifier>
      </xsl:when>
      <xsl:when test="string-length($provider-identifier) = 4">
        <dc:identifier xsi:type="oxnotation:department">
          <xsl:value-of select="upper-case($provider-identifier)"/>
        </dc:identifier>
      </xsl:when>
      <xsl:when test="string-length($provider-identifier) = 6">
        <dc:identifier xsi:type="oxnotation:twoThree">
          <xsl:value-of select="substring($provider-identifier, 5, 2)"/>
        </dc:identifier>
      </xsl:when>
      <xsl:when test="string-length($provider-identifier) = 8">
        <dc:identifier xsi:type="oxnotation:oxpoints">
          <xsl:value-of select="$provider-identifier"/>
        </dc:identifier>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>provider identifier '<xsl:value-of select="$provider-identifier"/>' not recognized.</xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Provider description -->
  <xsl:template match="txt_description" mode="provider">
   <dc:description>
      <xsl:apply-templates select="text()"/>
    </dc:description>
  </xsl:template>

  <!-- Provider title -->
  <xsl:template match="txt_ptitle" mode="provider">
    <dc:title>
      <xsl:apply-templates select="text()"/>
    </dc:title>
  </xsl:template>

  <!-- Provider URL -->
  <xsl:template match="txt_url" mode="provider">
    <mlo:url>
      <xsl:apply-templates select="text()"/>
    </mlo:url>
  </xsl:template>

  <!-- Course visibility -->
  <xsl:template match="cmb_visibility" mode="course-attribute">
    <xsl:variable name="visibility" select="normalize-space(.)"/>
    <xsl:choose>
      <xsl:when test="$visibility='PB'">
        <xsl:attribute name="oxcap:visibility">PB</xsl:attribute>
      </xsl:when>
      <xsl:when test="$visibility='RS'">
        <xsl:attribute name="oxcap:visibility">RS</xsl:attribute>
      </xsl:when>
      <xsl:when test="$visibility='PR'">
        <xsl:attribute name="oxcap:visibility">PR</xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>Course gives unknown visibility of <xsl:value-of select="$visibility"/></xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Course and presentation status -->
  <xsl:template match="cmb_status" mode="course-attribute presentation-attribute">
    <xsl:variable name="status" select="normalize-space(.)"/>
    <xsl:if test="string-length($status) gt 0 and not($status = 'CN')">
      <xsl:attribute name="oxcap:status">
        <xsl:value-of select="$status"/>
      </xsl:attribute>
    </xsl:if>
  </xsl:template>

  <!-- Course identifier -->
  <xsl:template match="txt_cidentifier" mode="course">
    <xsl:variable name="identifier" select="normalize-space(upper-case(.))"/>
    <dc:identifier>
      <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/course/</xsl:text>
      <xsl:value-of select="$identifier"/>
    </dc:identifier>
    <dc:identifier xsi:type="oxnotation:sharepoint-course">
      <xsl:value-of select="$identifier"/>
    </dc:identifier>
  </xsl:template>

  <!-- Course title -->
  <xsl:template match="txt_ctitle" mode="course">
    <dc:title>
      <xsl:value-of select="."/>
    </dc:title>
  </xsl:template>

  <!-- Course URL -->
  <xsl:template match="txt_curl" mode="course">
    <mlo:url>
      <xsl:value-of select="."/>
    </mlo:url>
  </xsl:template>

  <!-- Course skills -->
  <xsl:template match="group7" mode="course">
    <xsl:for-each select="list_skills[string-length(normalize-space(text())) gt 0]">
      <xsl:variable name="in" select="upper-case(normalize-space(.))"/>
      <xsl:variable name="subjectText">
        <xsl:choose>
          <xsl:when test="$in='CO'">Computing</xsl:when>
          <xsl:when test="$in='DA'">Data Analysis</xsl:when>
          <xsl:when test="$in='DM'">Data Management</xsl:when>
          <xsl:when test="$in='FW'">Field Work</xsl:when>
          <xsl:when test="$in='RD'">General Research Development</xsl:when>
          <xsl:when test="$in='IN'">Information Skills</xsl:when>
          <xsl:when test="$in='LS'">Laboratory Skills</xsl:when>
          <xsl:when test="$in='MM'">Mathematical Methods</xsl:when>
          <xsl:when test="$in='RM'">Research Methods</xsl:when>
          <xsl:when test="$in='ST'">Statistics</xsl:when>
          <xsl:when test="$in='TE'">Technical Skills</xsl:when>
          <xsl:when test="$in='CD'">Career Development</xsl:when>
          <xsl:when test="$in='PE'">Personal Effectiveness</xsl:when>
          <xsl:when test="$in='PS'">Presentation Skills</xsl:when>
          <xsl:when test="$in='ET'">Ethics</xsl:when>
          <xsl:when test="$in='IP'">Intellectual Property Skills</xsl:when>
          <xsl:when test="$in='IL'">Interpersonal</xsl:when>
          <xsl:when test="$in='RF'">Research and Financial Management</xsl:when>
          <xsl:when test="$in='HS'">Safety</xsl:when>
          <xsl:when test="$in='EE'">Enterprise and Enterpreneuership</xsl:when>
          <xsl:when test="$in='SC'">Seminars / Colloquia</xsl:when>
          <xsl:when test="$in='CS'">Communication Skills</xsl:when>
          <xsl:when test="$in='TA'">Teaching and Academic Skills</xsl:when>
        </xsl:choose>
      </xsl:variable>
      <dc:subject xmlns:ox-rdf="https://data.ox.ac.uk/id/ox-rdf/" identifier="{normalize-space(.)}" xsi:type="ox-rdf:notation">
        <xsl:value-of select="$subjectText"/>
      </dc:subject>
    </xsl:for-each>
  </xsl:template>

  <!-- Course subject -->
  <xsl:template match="txt_subject[text()]" mode="course">
    <dc:subject>
      <xsl:value-of select="."/>
    </dc:subject>
  </xsl:template>

  <!-- Course research methods -->
  <xsl:template match="group8" mode="course">
    <xsl:for-each select="researchmethods_drop">
      <xsl:variable name="rmIn" select="normalize-space(.)"/>
      <xsl:if test="string-length($rmIn) gt 0">
        <dc:subject xmlns:ox-rdf="https://data.ox.ac.uk/id/ox-rm/" identifier="{$rmIn}" xsi:type="ox-rm:notation">
          <xsl:variable name="rmText">
            <xsl:choose>
              <xsl:when test="$rmIn='QL'">Qualitative</xsl:when>
              <xsl:when test="$rmIn='QN'">Quantative</xsl:when>
            </xsl:choose>
          </xsl:variable>
          <xsl:value-of select="$rmText"/>
        </dc:subject>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <!-- Course requirements -->
  <xsl:template match="cmb_prerequisite" mode="course">
    <xsl:variable name="prerequisite" select="upper-case(normalize-space(.))"/>
    <regulations oxcap:eligibility="{$prerequisite}">
      <div xmlns="http://www.w3.org/1999/xhtml">
        <xsl:choose>
          <xsl:when test="$prerequisite = 'OX' or not(cmb_prerequisite)">
            <p>This course is available to the current students and staff of the University of Oxford.</p>
          </xsl:when>
          <xsl:when test="$prerequisite = 'ST'">
            <p>This course is available to the current staff of the University of Oxford.</p>
          </xsl:when>
          <xsl:when test="$prerequisite = 'PU'">
            <p>This course is available to the general public.</p>
          </xsl:when>
          <xsl:otherwise>
            <xsl:message>Error: cmb_prerequisite unknown value</xsl:message>
          </xsl:otherwise>
        </xsl:choose>
      </div>
    </regulations>
  </xsl:template>

  <!-- Learning outcomes -->
  <xsl:template match="txt_abstract[text()]" mode="course">
    <learningOutcomes>
      <xsl:value-of select="."/>
    </learningOutcomes>
  </xsl:template>

  <!-- Course description -->
  <xsl:template match="txt_ccdescription[xhtml:html]" mode="course">
    <dc:description>
      <div xmlns="http://www.w3.org/1999/xhtml">
        <xsl:apply-templates select="xhtml:html"/>
      </div>
    </dc:description>
  </xsl:template>

  <!-- Target/Intended audience -->
  <xsl:template match="txt_intended[text()]" mode="course">
    <dc:description xsi:type="courseDataProgramme:targetAudience">
      <xsl:value-of select="."/>
    </dc:description>
  </xsl:template>

  <!-- Application procedure with test for publicApplyTo-->
  <xsl:template match="txt_applyTo[text()]" mode="course">
    <applicationProcedure>
      <div xmlns="http://www.w3.org/1999/xhtml">
        <p>
          <xsl:text>University of Oxford members should apply via </xsl:text>
          <a href="{normalize-space(txt_applyTo)}"><xsl:value-of select="normalize-space(.)"/></a>
          <xsl:if test="string-length(normalize-space(../txt_publicapplyto)) gt 0">
            <xsl:text>, where applicable non-University members should apply via </xsl:text>
            <a href="{normalize-space(../txt_publicapplyto)}"><xsl:value-of select="normalize-space(../txt_publicapplyto)"/></a>
          </xsl:if>
          <xsl:text>.</xsl:text>
        </p>
      </div>
    </applicationProcedure>
  </xsl:template>

  <!-- Presentation identifier -->
  <xsl:template match="course_id[text()]" mode="presentation">
    <xsl:variable name="identifier" select="text()"/>
    <dc:identifier>
      <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/presentation/</xsl:text>
      <xsl:value-of select="$identifier"/>
    </dc:identifier>
    <dc:identifier xsi:type="oxnotation:sharepoint-presentation">
      <xsl:value-of select="$identifier"/>
    </dc:identifier>
  </xsl:template>

  <!-- Presentation start -->
  <xsl:template match="dt_start" mode="presentation">
    <mlo:start>
      <xsl:call-template name="xcri-date">
        <xsl:with-param name="date" select="normalize-space(text())"/>
        <xsl:with-param name="text" select="normalize-space(../txt_starttext/text())"/>
      </xsl:call-template>
    </mlo:start>
  </xsl:template>

  <!-- Presentation end -->
  <xsl:template match="dt_end" mode="presentation">
    <end>
      <xsl:call-template name="xcri-date">
        <xsl:with-param name="date" select="normalize-space(text())"/>
        <xsl:with-param name="text" select="normalize-space(../txt_endtext/text())"/>
      </xsl:call-template>
    </end>
  </xsl:template>

          <!--<xsl:variable name="durationValue"><xsl:value-of select="days-from-duration(xs:date(dt_end) - xs:date(dt_start))"/></xsl:variable>
                <xsl:variable name="approxDurationMonths"><xsl:value-of select=
                  "floor((xs:date(dt_end) - xs:date(dt_start)) div xs:dayTimeDuration('P30D'))"/></xsl:variable>
                <mlo:duration interval="{xs:date(dt_end) - xs:date(dt_start)}">Approximately <xsl:value-of select="$approxDurationMonths"/> months</mlo:duration>
                -->

  <!-- Member apply to -->
  <xsl:template match="txt_applyTo[text()]" mode="presentation">
    <oxcap:memberApplyTo>
      <xsl:value-of select="."/>
    </oxcap:memberApplyTo>
  </xsl:template>

  <!-- Public apply to -->
  <xsl:template match="txt_publicapplyto[text()]" mode="presentation">
    <applyTo>
      <xsl:value-of select="."/>
    </applyTo>
  </xsl:template>

  <!-- Venue -->
  <xsl:template match="txt_venue[text()]" mode="presentation">
    <venue>
      <provider>
        <xsl:choose>
          <xsl:when test="matches(., '^\d{8}$')">
            <dc:identifier xsi:type="oxnotation:oxpoints">
              <xsl:value-of select="."/>
            </dc:identifier>
          </xsl:when>
          <xsl:when test="matches(., '^\d{3}$')">
            <dc:identifier xsi:type="oxnotation:estates">
              <xsl:value-of select="."/>
            </dc:identifier>
          </xsl:when>
          <xsl:otherwise>
            <dc:title>
              <xsl:value-of select="."/>
            </dc:title>
          </xsl:otherwise>
        </xsl:choose>
      </provider>
    </venue>
  </xsl:template>

  <!-- Apply from -->
  <xsl:template match="dt_applyfrom" mode="presentation">
    <applyFrom>
      <xsl:call-template name="xcri-date">
        <xsl:with-param name="date" select="normalize-space(text())"/>
        <xsl:with-param name="text" select="normalize-space(../txt_applyfromtext/text())"/>
      </xsl:call-template>
    </applyFrom>
  </xsl:template>
  
  <!-- Apply from -->
  <xsl:template match="dt_applyuntil" mode="presentation">
    <applyFrom>
      <xsl:call-template name="xcri-date">
        <xsl:with-param name="date" select="normalize-space(text())"/>
        <xsl:with-param name="text" select="normalize-space(../txt_capplyuntiltext/text())"/>
      </xsl:call-template>
    </applyFrom>
  </xsl:template>

  <!-- Attendance mode-->
  <xsl:template match="txt_attendancemode" mode="presentation">
    <xsl:variable name="attendanceModeIn" select="normalize-space(.)"/>
    <attendanceMode identifier="{$attendanceModeIn}">
      <xsl:choose>
        <xsl:when test="$attendanceModeIn='CM'">Campus</xsl:when>
        <xsl:when test="$attendanceModeIn='DA'">Distance with attendance</xsl:when>
        <xsl:when test="$attendanceModeIn='DS'">Distance without attendance</xsl:when>
        <xsl:when test="$attendanceModeIn='NC'">Face-to-face non-campus</xsl:when>
        <xsl:when test="$attendanceModeIn='MM'">Mixed mode</xsl:when>
        <xsl:when test="$attendanceModeIn='ON'">Online (no attendance)</xsl:when>
        <xsl:when test="$attendanceModeIn='WB'">Work-based</xsl:when>
      </xsl:choose>
    </attendanceMode>
  </xsl:template>

  <!-- Attendance mode-->
  <xsl:template match="cmb_pattern" mode="presentation">
    <xsl:variable name="attendancePatternIn" select="normalize-space(.)"/>
    <attendancePattern identifier="{$attendancePatternIn}">
      <xsl:choose>
        <xsl:when test="$attendancePatternIn='DT'">Daytime</xsl:when>
        <xsl:when test="$attendancePatternIn='EV'">Evening</xsl:when>
        <xsl:when test="$attendancePatternIn='TW'">Twilight</xsl:when>
        <xsl:when test="$attendancePatternIn='DR'">Day/Block release</xsl:when>
        <xsl:when test="$attendancePatternIn='WE'">Weekend</xsl:when>
        <xsl:when test="$attendancePatternIn='CS'">Customised</xsl:when>
      </xsl:choose>
    </attendancePattern>
  </xsl:template>

  <!-- Number of places -->
  <xsl:template match="txt_places[text()]" mode="presentation">
    <mlo:places>
      <xsl:value-of select="."/>
    </mlo:places>
  </xsl:template>

  <xsl:template match="group5" mode="presentation">
    <xsl:variable name="presentation-identifier" select="../course_id/text()"/>
    <xsl:for-each select="group6">
            <xsl:if test="normalize-space(dt_sessionid) and normalize-space(tm_sessionid_starttime)">
              <!-- Time fields have a date component, presumably the date when the field was updated.
                     Here, we replace it with the date from dt_sessionid -->
              <xsl:variable name="start" select="concat(normalize-space(dt_sessionid), 'T', substring-after(normalize-space(tm_sessionid_starttime), 'T'))"/>
              <xsl:variable name="end" select="concat(normalize-space(dt_sessionid), 'T', substring-after(normalize-space(tm_sessionid_endtime), 'T'))"/>
              <oxcap:session>
                <dc:identifier>
                  <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/session/</xsl:text>
                  <xsl:value-of select="concat($presentation-identifier, '/', txt_sessionid)"/>
                </dc:identifier>
                <dc:identifier xsi:type="oxnotation:sharepoint-session">
                  <xsl:value-of select="concat($presentation-identifier, '/', txt_sessionid)"/>
                </dc:identifier>
                <mlo:start dtf="{$start}">
                  <xsl:value-of select="format-dateTime(xs:dateTime($start), '[F] [D] [MNn] [Y] at [H]:[m]')"/>
                </mlo:start>
                <xsl:if test="normalize-space(tm_sessionid_endtime)">
                  <end dtf="{$end}">
                    <xsl:value-of select="format-dateTime(xs:dateTime($end), '[F] [D] [MNn] [Y] at [H]:[m]')"/>
                  </end>
                </xsl:if>
              </oxcap:session>
            </xsl:if>
          </xsl:for-each>
  </xsl:template>

  <!-- Pass through HTML -->
  <xsl:template match="xhtml:html">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="xhtml:*">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!-- Catch-all -->
  <xsl:template match="*|@*" mode="#all"/>


  <xsl:template name="xcri-date">
    <xsl:param name="date"/>
    <xsl:param name="text"/>
    <xsl:if test="$date">
      <xsl:attribute name="dtf">
        <xsl:value-of select="$date"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="$text">
        <xsl:value-of select="$text"/>
      </xsl:when>
      <xsl:when test="$date">
        <xsl:value-of select="format-date(xs:date($date), '[F] [D] [MNn] [Y]')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>Error: Missing date!</xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
