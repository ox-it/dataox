<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://xcri.org/profiles/1.2/catalog" 
    xmlns:xcriTerms="http://xcri.org/profiles/catalog/terms"
    xmlns:xcri="http://xcri.org/profiles/1.2/catalog"
    xmlns:xhtml="http://www.w3.org/1999/xhtml" 
    xmlns:dc="http://purl.org/dc/elements/1.1/" 
    xmlns:dcterms="http://purl.org/dc/terms/" 
    xmlns:oxcap="http://purl.ox.ac.uk/oxcap/ns/"
    xmlns:credit="http://purl.org/net/cm" 
    xmlns:mlo="http://purl.org/net/mlo" 
    xmlns:courseDataProgramme="http://xcri.co.uk"
    xmlns:oxnotation="https://data.ox.ac.uk/id/notation/"
    xmlns:ox-rm="https://data.ox.ac.uk/id/ox-rm/"
    xmlns:ox-rdf="https://data.ox.ac.uk/id/ox-rdf/"
    xpath-default-namespace="http://schemas.microsoft.com/office/infopath/2003/myXSD/2012-03-17T23:37:18"
    version="2.0">
  <xsl:output indent="yes"/>
  
  
  <!-- Should we change so stylesheet iterates over all files in the directory? Or just call multiple times (e.g. for file in *.xml) -->
  
  <xsl:template match="myFields">
      <provider>
        <xsl:choose>
            <xsl:when test="txt_description"><dc:description><xsl:apply-templates select="txt_description"/></dc:description></xsl:when>
            <xsl:otherwise><dc:description>University of Oxford</dc:description></xsl:otherwise>
        </xsl:choose>
        <!--<xsl:if test="txt_url"><dc:identifier><xsl:value-of select="txt_url"/></dc:identifier></xsl:if>-->
        
        <xsl:variable name="provider-identifier" select="normalize-space(txt_identifier)"/>
        <dc:identifier>
          <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/provider/</xsl:text>
          <xsl:value-of select="$provider-identifier"/>
        </dc:identifier>
        <xsl:choose>
          <xsl:when test="string-length($provider-identifier) = 2">
            <dc:identifier xsi:type="oxnotation:twoThree"><xsl:value-of select="upper-case($provider-identifier)"/></dc:identifier>
          </xsl:when>
          <xsl:when test="string-length($provider-identifier) = 4">
            <dc:identifier xsi:type="oxnotation:department"><xsl:value-of select="upper-case($provider-identifier)"/></dc:identifier>
          </xsl:when>
          <xsl:when test="string-length($provider-identifier) = 6">
            <dc:identifier xsi:type="oxnotation:twoThree"><xsl:value-of select="substring($provider-identifier, 5, 2)"/></dc:identifier>
          </xsl:when>
          <xsl:when test="string-length($provider-identifier) = 8">
            <dc:identifier xsi:type="oxnotation:oxpoints"><xsl:value-of select="$provider-identifier"/></dc:identifier>
          </xsl:when>
          <xsl:otherwise>
            <xsl:message>provider identifier '<xsl:value-of select="$provider-identifier"/>' not recognized.</xsl:message>
          </xsl:otherwise>
        </xsl:choose>
          
        
        <!-- ptitle -->
        <dc:title><xsl:value-of select="txt_ptitle"/></dc:title>
        
        <mlo:url><xsl:value-of select="txt_url"/></mlo:url>
    
    
    <!-- course, with oxcap:visibility and possibly oxcap:status attributes -->
        <course><xsl:choose>
              <xsl:when test="normalize-space(cmb_visibility)='PB' or not(cmb_visibility)"><xsl:attribute name="oxcap:visibility">PB</xsl:attribute></xsl:when>
              <xsl:when test="normalize-space(cmb_visibility)='RS'"><xsl:attribute name="oxcap:visibility">RS</xsl:attribute></xsl:when>
              <xsl:when test="normalize-space(cmb_visibility)='PR'"><xsl:attribute name="oxcap:visibility">PR</xsl:attribute></xsl:when>
              <xsl:otherwise><xsl:message>
                  Course gives unknown visibility of <xsl:value-of select="cmb_visibility"/></xsl:message></xsl:otherwise>
          </xsl:choose>
            <xsl:if test="string-length(normalize-space(cmb_status)) gt 0 and not(normalize-space(cmb_status) = 'CN')"><xsl:attribute name="oxcap:status"><xsl:value-of select="normalize-space(cmb_status)"/></xsl:attribute></xsl:if>

            <dc:identifier>
              <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/course/</xsl:text>
              <xsl:value-of select="txt_cidentifier"/>
            </dc:identifier>
            <dc:identifier xsi:type="oxnotation:sharepoint-course">
              <xsl:value-of select="txt_cidentifier"/>
            </dc:identifier>
            
            <dc:title><xsl:value-of select="txt_ctitle"/></dc:title>
            <mlo:url><xsl:value-of select="txt_curl"/></mlo:url>
          
          <!-- all are graduate training -->
          <dc:subject xsi:type="ox-rdf:notation" identifier="GT">Graduate Training</dc:subject>
          <!-- subject -->
            <xsl:if test="string-length(normalize-space(txt_subject)) gt 0"><dc:subject><xsl:value-of select="txt_subject"/></dc:subject></xsl:if>
            
          <!-- skills -->
            <xsl:for-each select="group7/list_skills[string-length(normalize-space(text())) gt 0]">
              <xsl:variable name="in" select="upper-case(normalize-space(.))"/>
              <xsl:variable name="subjectText"><xsl:choose>
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
              </xsl:choose></xsl:variable>
              <dc:subject identifier="{normalize-space(.)}"  xsi:type="ox-rdf:notation" 
                xmlns:ox-rdf="https://data.ox.ac.uk/id/ox-rdf/"><xsl:value-of select="$subjectText"/></dc:subject>    
            </xsl:for-each>
            
            <!-- research methods -->
            <xsl:variable name="rmIn" select="normalize-space(researchmethods_drop)"/>
            <xsl:if test="string-length($rmIn) gt 0">
              <dc:subject identifier="{$rmIn}" 
                xsi:type="ox-rm:notation" 
                xmlns:ox-rdf="https://data.ox.ac.uk/id/ox-rm/">
                <xsl:variable name="rmText">
                  <xsl:choose>
                    <xsl:when test="$rmIn='QL'">Qualitative</xsl:when>
                    <xsl:when test="$rmIn='QN'">Quantative</xsl:when>
                  </xsl:choose>
                </xsl:variable><xsl:value-of select="$rmText"/></dc:subject>
            </xsl:if>
            
            
            <!-- prerequisite e.g. regulations -->
            <regulations oxcap:eligibility="{normalize-space(cmb_prerequisite)}">
              <div xmlns="http://www.w3.org/1999/xhtml">
                <xsl:choose>
                  <xsl:when test="upper-case(normalize-space(cmb_prerequisite)) = 'OX' or not(cmb_prerequisite)"><p>This course is available to the current students and staff of the University of Oxford.</p></xsl:when>
                  <xsl:when test="upper-case(normalize-space(cmb_prerequisite)) = 'ST'"><p>This course is available to the current staff of the University of Oxford.</p></xsl:when>
                  <xsl:when test="upper-case(normalize-space(cmb_prerequisite)) = 'PU'"><p>This course is available to the general public.</p></xsl:when>
                  <xsl:otherwise><xsl:message>Error: cmb_prerequisite unknown value</xsl:message></xsl:otherwise>
                </xsl:choose>
              </div>
            </regulations>
            
            <!-- learning outcomes if it exists -->
            <xsl:if test="string-length(normalize-space(txt_abstract)) gt 0">
              <learningOutcomes><xsl:apply-templates select="txt_abstract"/></learningOutcomes>
            </xsl:if>
            
                        
            <!-- description with intended audience added -->
            <xsl:if test="txt_ccdescription/xhtml:html">
              <dc:description>
                <div xmlns="http://www.w3.org/1999/xhtml">
                  <xsl:apply-templates  select="txt_ccdescription/xhtml:html"/>
                  <xsl:if test="string-length(normalize-space(txt_intended)) gt 0"><xhtml:p>Intended Audience: <xsl:apply-templates select="txt_intended"/></xhtml:p></xsl:if>
                </div>
              </dc:description>
            </xsl:if>
           
           <!-- Application procedure with test for publicApplyTo-->
            <applicationProcedure>
              <div xmlns="http://www.w3.org/1999/xhtml">
                <p>
                  University of Oxford members should apply via <a href="{normalize-space(txt_applyTo)}"> <xsl:value-of select="normalize-space(txt_applyTo)"/></a><xsl:if test="string-length(normalize-space(txt_publicapplyto)) gt 0">, where applicable non-University members should apply via <a href="{normalize-space(txt_publicapplyto)}"><xsl:value-of select="normalize-space(txt_publicapplyto)"/></a></xsl:if>.
                </p>
              </div>
            </applicationProcedure>
            
            
        <!-- presentation with oxcap:status if CN -->            
            <presentation><xsl:if test="string-length(normalize-space(cmb_status)) gt 0 and normalize-space(cmb_status) = 'CN'"><xsl:attribute name="oxcap:status"><xsl:value-of select="normalize-space(cmb_status)"/></xsl:attribute></xsl:if>
              <dc:identifier>
                <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/presentation/</xsl:text>
                <xsl:value-of select="txt_cidentifier"/>
              </dc:identifier>
              <dc:identifier xsi:type="oxnotation:sharepoint-presentation">
                <xsl:value-of select="txt_cidentifier"/>
              </dc:identifier>

              <!--<dc:identifier ><xsl:value-of select="txt_curl"/></dc:identifier>-->
              
              <!-- Start /end -->
              <mlo:start><xsl:if test="dt_start"><xsl:attribute name="dtf"><xsl:value-of select="normalize-space(dt_start)"/></xsl:attribute></xsl:if>
                <xsl:choose>
                  <xsl:when test="string-length(normalize-space(txt_applyfromtext)) gt 0"><xsl:value-of  select="txt_starttext"/></xsl:when>
                  <xsl:when test="dt_start"><xsl:value-of select="format-date(xs:date(dt_start), '[F] [D] [MNn] [Y]')"/></xsl:when>
                  <xsl:otherwise><xsl:message>Error: Missing start date!</xsl:message></xsl:otherwise>
                </xsl:choose>
              </mlo:start>
              <end><xsl:if test="dt_end"><xsl:attribute name="dtf"><xsl:value-of select="normalize-space(dt_end)"/></xsl:attribute></xsl:if>
                <xsl:choose>
                  <xsl:when test="dt_end"><xsl:value-of select="format-date(xs:date(dt_end), '[F] [D] [MNn] [Y]')"/></xsl:when>
                  <xsl:otherwise><xsl:message>Error: Missing end date!</xsl:message></xsl:otherwise>
                </xsl:choose>
              </end>
              <!--<xsl:variable name="durationValue"><xsl:value-of select="days-from-duration(xs:date(dt_end) - xs:date(dt_start))"/></xsl:variable>
                <xsl:variable name="approxDurationMonths"><xsl:value-of select=
                  "floor((xs:date(dt_end) - xs:date(dt_start)) div xs:dayTimeDuration('P30D'))"/></xsl:variable>
                <mlo:duration interval="{xs:date(dt_end) - xs:date(dt_start)}">Approximately <xsl:value-of select="$approxDurationMonths"/> months</mlo:duration>
                -->
              
              <!-- Applyto/public apply to -->
              <oxcap:memberApplyTo><xsl:value-of select="txt_applyTo"/></oxcap:memberApplyTo>
              <applyTo><xsl:value-of select="txt_publicapplyto"/></applyTo>
              
                    
            
            <!-- Venue -->
            <venue>
                <provider>
                  <dc:identifier xsi:type="oxnotation:oxpoints"><xsl:value-of select="txt_venue"/></dc:identifier>
                </provider>
              </venue>
                       
              <!-- apply from/until with formatted date if text not provided -->
              <applyFrom><xsl:if test="dt_applyfrom"><xsl:attribute name="dtf"><xsl:value-of select="normalize-space(dt_applyfrom)"/></xsl:attribute></xsl:if>
                <xsl:choose>
                  <xsl:when test="string-length(normalize-space(txt_applyfromtext)) gt 0"><xsl:value-of  select="txt_applyfromtext"/></xsl:when>
                  <xsl:when test="dt_applyfrom[not(@xsi:nil)]"><xsl:value-of select="format-date(xs:date(dt_applyfrom), '[F] [D] [MNn] [Y]')"/></xsl:when>
                  <xsl:otherwise><xsl:message>Error: Missing start date!</xsl:message></xsl:otherwise>
                </xsl:choose>
              </applyFrom>
              <applyUntil><xsl:if test="dt_applyuntil"><xsl:attribute name="dtf"><xsl:value-of select="normalize-space(dt_applyuntil)"/></xsl:attribute></xsl:if>
                <xsl:choose>
                  <xsl:when test="string-length(normalize-space(txt_capplyuntiltext)) gt 0"><xsl:value-of  select="txt_capplyuntiltext"/></xsl:when>
                  <xsl:when test="dt_applyuntil[not(@xsi:nil)]"><xsl:value-of select="format-date(xs:date(dt_applyuntil), '[F] [D] [MNn] [Y]')"/></xsl:when>
                  <xsl:otherwise><xsl:message>Error: Missing end date!</xsl:message></xsl:otherwise>
                </xsl:choose>
              </applyUntil>
              
            
            <!-- Attendance mode / pattern-->
              <xsl:variable name="attendanceModeIn" select="normalize-space(txt_attendancemode)"/>
              <attendanceMode identifier="{$attendanceModeIn}">
                <xsl:variable name="attendanceModeText">
                  <xsl:choose>
                    <xsl:when test="$attendanceModeIn='CM'">Campus</xsl:when>
                    <xsl:when test="$attendanceModeIn='DA'">Distance with attendance</xsl:when>
                    <xsl:when test="$attendanceModeIn='DS'">Distance without attendance</xsl:when>
                    <xsl:when test="$attendanceModeIn='NC'">Face-to-face non-campus</xsl:when>
                    <xsl:when test="$attendanceModeIn='MM'">Mixed mode</xsl:when>
                    <xsl:when test="$attendanceModeIn='ON'">Online (no attendance)</xsl:when>
                    <xsl:when test="$attendanceModeIn='WB'">Work-based</xsl:when>
                  </xsl:choose>
                </xsl:variable><xsl:value-of select="$attendanceModeText"/></attendanceMode>
              <xsl:variable name="attendancePatternIn" select="normalize-space(cmb_pattern)"/>
              <attendancePattern identifier="{$attendancePatternIn}">
                <xsl:variable name="attendancePatternText">
                  <xsl:choose>
                    <xsl:when test="$attendancePatternIn='DT'">Daytime</xsl:when>
                    <xsl:when test="$attendancePatternIn='EV'">Evening</xsl:when>
                    <xsl:when test="$attendancePatternIn='TW'">Twilight</xsl:when>
                    <xsl:when test="$attendancePatternIn='DR'">Day/Block release</xsl:when>
                    <xsl:when test="$attendancePatternIn='WE'">Weekend</xsl:when>
                    <xsl:when test="$attendancePatternIn='CS'">Customised</xsl:when>
                  </xsl:choose>
                </xsl:variable><xsl:value-of select="$attendancePatternText"/></attendancePattern>
        
              <xsl:if test="string-length(normalize-space(txt_places)) gt 0">
                <mlo:places>
                  <xsl:value-of select="txt_places"/>
                </mlo:places>
              </xsl:if>
            </presentation>
            
            <xsl:if test="group5/group6">
              <xsl:for-each select="group5/group6">
                <oxcap:session>
                  <dc:identifier>
                    <xsl:text>https://course.data.ox.ac.uk/id/sharepoint/session/</xsl:text>
                    <xsl:value-of select="../../txt_cidentifier"/>
                    <xsl:text>/</xsl:text>
                    <xsl:value-of select="txt_sessionid"/>
                  </dc:identifier>
                  <dc:identifier xsi:type="oxnotation:sharepoint-session">
                    <xsl:value-of select="txt_cidentifier"/>
                    <xsl:text>-</xsl:text>
                    <xsl:value-of select="txt_sessionid"/>
                  </dc:identifier>
                  <mlo:start dtf="{normalize-space(tm_sessionid_starttime)}">
                    <xsl:value-of select="format-dateTime(xs:dateTime(tm_sessionid_starttime), '[F] [D] [MNn] [Y] at [H]:[m]')"/>
                  </mlo:start>
                  <end dtf="{normalize-space(tm_sessionid_endtime)}">
                    <xsl:value-of select="format-dateTime(xs:dateTime(tm_sessionid_endtime), '[F] [D] [MNn] [Y] at [H]:[m]')"/>
                  </end>
                  </oxcap:session>
                </xsl:for-each>
            </xsl:if>
            
            </presentation>
            
          </course>
      </provider>
  </xsl:template>
  <xsl:template match="xhtml:html">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="xhtml:*">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="/">
    <catalog
        xsi:schemaLocation="http://xcri.org/profiles/1.2/catalog http://www.xcri.co.uk/bindings/xcri_cap_1_2.xsd http://xcri.org/profiles/1.2/catalog/terms  http://www.xcri.co.uk/bindings/xcri_cap_terms_1_2.xsd http://xcri.co.uk http://www.xcri.co.uk/bindings/coursedataprogramme.xsd" 
        generated="{current-dateTime()}">
      <dc:title>Course data stored in SharePoint</dc:title>
      <dc:provider>
        <dc:identifier xsi:type="oxnotation:oxpoints">31337175</dc:identifier>
      </dc:provider>
      <dc:identifier>https://course.data.ox.ac.uk/id/sharepoint/catalogue</dc:identifier>
      <dc:contributor><xsl:value-of select="txt_ptitle"/></dc:contributor>
      <dc:description>from SP InfoPath docs</dc:description>

      <xsl:apply-templates select=".//myFields"/>
    </catalog>
  </xsl:template>

</xsl:stylesheet>
