<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:oo="http://purl.org/openorg/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    xmlns:cat="http://purl.org/NET/catalogue/"
    xmlns:ex="http://www.example.org/"
    xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
    xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
    xpath-default-namespace="https://github.com/ox-it/python-sharepoint/"
    version="2.0">
  <xsl:import href="common.xsl"/>
  <xsl:output method="xml" indent="yes"/>

  <xsl:param name="store"/>
  <xsl:variable name="internal" select="$store='itservices'"/>

  <xsl:key name="user-bases" match="/site/lists/list[@name='User bases']/rows/row" use="@id"/>
  <xsl:key name="user-base-names" match="/site/lists/list[@name='User bases']/rows/row" use="fields/field[@name='Title']/text/text()"/>
  <xsl:key name="grouped-services" match="/site/lists/list[@name='Service Catalogue']/rows/row" use="fields/field[@name='Service_x0020_group']/lookup/@id"/>
  <xsl:key name="services" match="/site/lists/list[@name='Service Catalogue']/rows/row" use="@id"/>

  <xsl:function name="ex:include-service">
    <xsl:param name="row"/>
      <xsl:if test="not($row//field[@name='Redact']/boolean='true') and (
                 $store='itservices' or (
                         $row//field[@name='Viewable_x0020_by']/text[not(text()='IT Services')]
                     and $row//field[@name='Archived']/text = 'Live'
                     and $row//field[@name='Service_x0020_type']/text = 'Customer facing service'))">true</xsl:if>
    <!--<xsl:choose>
      <xsl:when test="$row//field[@name='Redact']/boolean='true'"/>
      <xsl:when test="$store='itservices'">true</xsl:when>
      <xsl:when test="$row//field[@name='Service_x0020_group_x0020_or_x00']/text/text() = 'Service grouping'"/>
      <xsl:when test="$row//field[@name='Viewable_x0020_by']/text[not(text()='IT Services')]">true</xsl:when>
    </xsl:choose>-->
  </xsl:function>

  <xsl:template match="list[@name='Service Catalogue']/rows">
    <gr:BusinessEntity rdf:about="{$it-services}">
      <xsl:for-each select="row">
        <xsl:if test="ex:include-service(.)">
          <gr:offers>
            <xsl:apply-templates select="."/>
          </gr:offers>
        </xsl:if>
      </xsl:for-each>
    </gr:BusinessEntity>
    <xsl:for-each select="row">
      <xsl:if test="ex:include-service(.)">
        <cat:Record rdf:about="{ex:service-uri('service-catalogue-record', .)}">
          <xsl:apply-templates select="." mode="in-catalogue-record"/>
          <cat:catalogue rdf:resource="https://id.it.ox.ac.uk/service-catalogue"/>
          <cat:item rdf:resource="{ex:service-uri('service', .)}"/>
        </cat:Record>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="list[@name='Service Catalogue']/rows/row">
    <gr:Offering rdf:about="{ex:service-uri('service-offering', .)}">
      <gr:hasBusinessFunction rdf:resource="http://purl.org/goodrelations/v1#ProvideService"/>
      <gr:includes>
        <gr:ProductOrService rdf:about="{ex:service-uri('service', .)}">
          <rdf:type rdf:resource="http://spi-fm.uca.es/neologism/cerif#Service"/>
          <oo:organizationPart rdf:resource="{$it-services}"/>
          <oo:formalOrganization rdf:resource="{$university-of-oxford}"/>
          <xsl:apply-templates mode="in-service"/>
        </gr:ProductOrService>
      </gr:includes>
      <xsl:apply-templates mode="in-offering"/>
    </gr:Offering>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]" mode="in-service">
    <rdfs:label>
      <xsl:value-of select="text()"/>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]" mode="in-offering">
    <rdfs:label>
      <xsl:value-of select="text()"/>
      <xsl:text> (service offering)</xsl:text>
    </rdfs:label>
  </xsl:template>

  <xsl:template match="field[@name='Description']/text[text()]" mode="in-service">
    <rdfs:comment rdf:datatype="http://purl.org/xtypes/Fragment-HTML">
      <xsl:text>&lt;div&gt;</xsl:text>
      <xsl:value-of select="text()"/>
      <xsl:text>&lt;/div&gt;</xsl:text>
    </rdfs:comment>
  </xsl:template>

  <xsl:template match="field[@name='Keywords']/text[text()]" mode="in-service">
    <xsl:for-each select="tokenize(text(), ',')">
      <dc:subject>
        <xsl:value-of select="normalize-space(.)"/>
      </dc:subject>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_URL']/url" mode="in-service">
    <foaf:homepage rdf:resource="{@href}"/>
  </xsl:template>

  <xsl:template match="field[@name='Documentation_x0020_URL']/url" mode="in-service">
    <adhoc:serviceInformationPage rdf:resource="{@href}"/>
  </xsl:template>

  <xsl:template match="field[@name='Published_x0020_SLA_x0020_or_x00']/url" mode="in-service">
    <adhoc:serviceLevelDefinition rdf:resource="{@href}"/>
  </xsl:template>

  <!-- Use this field to go up and re-interpret the row in the contact of its contact information -->
  <xsl:template match="field[@name='Initial_x0020_contact_x0020_phon']" mode="in-service">
    <xsl:apply-templates select="../.." mode="service-contact"/>
  </xsl:template>
  <!-- Only create a contact agent if one of the three contact fields is filled -->
  <xsl:template match="list[@name='Service Catalogue']/rows/row" mode="service-contact">
    <xsl:if test="fields/field[@name='Initial_x0020_contact_x0020_phon' or @name='Initial_x0020_Contact_x0020_Emai' or @name='Initial_x0020_Contact_x0020_Form']/*/text()">
      <oo:contact>
        <foaf:Agent rdf:about="{ex:service-uri('service', .)}/contact">
          <xsl:apply-templates select="fields/field[*/text()]" mode="service-contact"/>
        </foaf:Agent>
      </oo:contact>
    </xsl:if>
  </xsl:template>
  <xsl:template match="field[@name='Initial_x0020_contact_x0020_phon']/text" mode="service-contact">
    <xsl:call-template name="telephone-extension"/>
  </xsl:template>
  <xsl:template match="field[@name='Initial_x0020_Contact_x0020_Emai']" mode="service-contact">
    <xsl:for-each select="tokenize(text/text(), '\s+')">
      <v:email rdf:resource="mailto:{.}"/>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="field[@name='Initial_x0020_Contact_x0020_Form']" mode="service-contact">
    <xsl:for-each select="tokenize(url/@href, '\s+')">
      <oo:contactForm rdf:resource="{.}"/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="field[@name='Activities']/text" mode="in-service">
    <xsl:variable name="id">
      <xsl:choose>
        <xsl:when test="text() = 'Administration'">1</xsl:when>
        <xsl:when test="text() = 'Core infrastructure'">2</xsl:when>
        <xsl:when test="text() = 'Research'">3</xsl:when>
        <xsl:when test="text() = 'Teaching'">4</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$id">
        <dcterms:subject rdf:resource="{$base-uri}service-activity-category/{$id}"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>Unexpected activity category: <xsl:value-of select="text()"/></xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_type']/text" mode="in-service">
    <xsl:variable name="id">
      <xsl:choose>
        <xsl:when test="text() = 'Customer facing service'">user-facing</xsl:when>
        <xsl:when test="text() = 'Supporting service'">supporting</xsl:when>
        <xsl:when test="text() = 'ITSS only'">itss</xsl:when>
        <xsl:when test="text() = 'Internal only'">internal</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$id">
        <dcterms:subject rdf:resource="{$base-uri}service-type/{$id}"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>Unexpected service type: <xsl:value-of select="text()"/></xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="field[@name='Archived']/text" mode="in-service">
    <xsl:variable name="id">
      <xsl:choose>
        <xsl:when test="text() = 'In development'">in-development</xsl:when>
        <xsl:when test="text() = 'Live'">production</xsl:when>
        <xsl:when test="text() = 'Production'">production</xsl:when>
        <xsl:when test="text() = 'Deprecated'">itss</xsl:when>
        <xsl:when test="text() = 'Archived'">withdrawn</xsl:when>
        <xsl:when test="text() = 'Withdrawn'">withdrawn</xsl:when>
        <xsl:when test="text() = 'Costing roll-up only'"/>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$id">
        <dcterms:subject rdf:resource="{$base-uri}service-lifecycle-status/{$id}"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>Unexpected service lifecycle status: <xsl:value-of select="text()"/></xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_classification']/lookup" mode="in-service">
    <dcterms:subject rdf:resource="{ex:service-classification-uri(.)}"/>
  </xsl:template>
  
  <xsl:template match="field[@name='Service_x0020_Delivery_x0020_Man']/lookup" mode="in-service">
    <xsl:if test="$internal">
      <adhoc:serviceTeam rdf:resource="{ex:team-uri(.)}"/>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="field[@name='GenericUserBases']/text" mode="in-offering">
    <xsl:variable name="user-base-uri" select="key('user-base-names', text())/fields/field[@name='URI']/text/text()"/>
    <xsl:if test="$user-base-uri">
      <gr:eligibleCustomerTypes rdf:resource="{$user-base-uri}"/>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="field[@name='Generic_x0020_user_x0020_bases']/lookup" mode="in-offering">
    <xsl:variable name="user-base-uri" select="key('user-bases', @id)/fields/field[@name='URI']/text/text()"/>
    <xsl:if test="$user-base-uri">
      <gr:eligibleCustomerTypes rdf:resource="{$user-base-uri}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Specific_x0020_user_x0020_bases']/user" mode="in-offering">
    <gr:eligibleCustomerTypes rdf:resource="{ex:agent-uri(.)}"/>
  </xsl:template>

  <xsl:template match="field[@name='Escalate_x0020_to']/user" mode="in-service">
    <xsl:if test="$internal">
      <adhoc:serviceEscalationContact rdf:resource="{ex:agent-uri(.)}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_Owner']/user" mode="in-service">
    <xsl:if test="$internal">
      <adhoc:serviceOwner rdf:resource="{ex:agent-uri(.)}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Business_x0020_Owner']/user" mode="in-service">
    <xsl:if test="$internal">
      <adhoc:serviceBusinessOwner rdf:resource="{ex:agent-uri(.)}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Slug']/text" mode="in-service">
    <skos:notation rdf:datatype="https://id.it.ox.ac.uk/notation/service">
      <xsl:choose>
        <xsl:when test="text()">
          <xsl:value-of select="text()"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="../../../@id"/>
        </xsl:otherwise>
      </xsl:choose>
    </skos:notation>
  </xsl:template>
  
  <xsl:template match="field[@name='Status_x0020_ID']/text[text()]" mode="in-service">
    <foaf:account>
      <foaf:OnlineAccount>
        <foaf:accountServiceHomepage rdf:resource="http://status.ox.ac.uk/"/>
        <foaf:accountName>
          <xsl:value-of select="text()"/>
        </foaf:accountName>
      </foaf:OnlineAccount>
    </foaf:account>
    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/status-ox-ac-uk-service">
      <xsl:value-of select="text()"/>
    </skos:notation>
  </xsl:template>

  <xsl:template match="field[@name='Twitter']/text[text()]" mode="in-service">
    <foaf:account>
      <foaf:OnlineAccount rdf:about="https://www.twitter.com/{text()}">
        <foaf:accountServiceHomepage rdf:resource="https://www.twitter.com/"/>
        <foaf:accountName>
          <xsl:value-of select="text()"/>
        </foaf:accountName>
      </foaf:OnlineAccount>
    </foaf:account>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]" mode="in-activity-category">
    <skos:prefLabel>
      <xsl:value-of select="text()"/>
    </skos:prefLabel>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_group']/lookup[@id != '0']" mode="in-service">
    <xsl:variable name="part-of" select="key('services', @id)"/>
    <xsl:if test="$part-of and ex:include-service($part-of)">
      <dcterms:isPartOf rdf:resource="{ex:service-uri('service', $part-of)}"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_group_x0020_or_x00']/text" mode="in-service">
    <xsl:for-each select="key('grouped-services', ../../../@id)">
      <dcterms:hasPart rdf:resource="{ex:service-uri('service', .)}"/>
    </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="field[@name='Modified']/dateTime/text()" mode="in-catalogue-record">
    <dcterms:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">
      <xsl:copy/>
    </dcterms:modified>
  </xsl:template>
  
  <xsl:template match="field[@name='Created']/dateTime/text()" mode="in-catalogue-record">
    <dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">
      <xsl:copy/>
    </dcterms:created>
  </xsl:template>
  
  <xsl:template match="field[@name='CatalogueReady']/boolean/text()" mode="in-catalogue-record">
    <adhoc:catalogueReady rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">
      <xsl:copy/>
    </adhoc:catalogueReady>
  </xsl:template>
</xsl:stylesheet>
