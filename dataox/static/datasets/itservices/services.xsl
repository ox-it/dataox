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
    xmlns:tio="http://purl.org/tio/ns#"
    xmlns:v="http://www.w3.org/2006/vcard/ns#"
    xmlns:ex="http://www.example.org/"
    xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
    xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
    xpath-default-namespace="https://github.com/ox-it/python-sharepoint/"
    version="2.0">
  <xsl:import href="common.xsl"/>
  <xsl:output method="xml" indent="yes"/>

  <xsl:param name="store"/>
  <xsl:variable name="internal" select="$store='itservices'"/>

  <xsl:variable name="service-base-uri">https://data.ox.ac.uk/id/itservices/</xsl:variable>

  <xsl:key name="user-bases" match="/site/lists/list[@name='User bases']/rows/row" use="@id"/>
  <xsl:key name="user-base-names" match="/site/lists/list[@name='User bases']/rows/row" use="fields/field[@name='Title']/text/text()"/>
  <xsl:key name="grouped-services" match="/site/lists/list[@name='Service Catalogue']/rows/row" use="fields/field[@name='Service_x0020_group']/lookup/@id"/>

  <xsl:template match="list[@name='Service Catalogue']/rows">
    <gr:BusinessEntity rdf:about="{$it-services}">
      <xsl:for-each select="row">
        <xsl:if test="not(.//field[@name='Redact']/boolean='true') and (
                   $store='itservices' or (
                           .//field[@name='Viewable_x0020_by']/text[not(text()='IT Services')]
                       and .//field[@name='Archived']/text = 'Live'
                       and .//field[@name='Service_x0020_type']/text = 'Customer facing service'))">
          <gr:offers>
            <xsl:apply-templates select="."/>
          </gr:offers>
        </xsl:if>
      </xsl:for-each>
    </gr:BusinessEntity>
  </xsl:template>

  <xsl:template match="list[@name='Service Catalogue']/rows/row">
    <gr:Offering rdf:about="{$service-base-uri}service-offering/{@id}">
      <gr:includes>
        <tio:TicketPlaceholder rdf:about="{$service-base-uri}use-of-service/{@id}">
          <tio:accessTo>
            <gr:ProductOrService rdf:about="{$service-base-uri}service/{@id}">
              <rdf:type rdf:resource="http://spi-fm.uca.es/neologism/cerif#Service"/>
              <oo:organizationPart rdf:resource="{$it-services}"/>
              <oo:formalOrganization rdf:resource="{$university-of-oxford}"/>
              <xsl:apply-templates mode="in-service"/>
            </gr:ProductOrService>
          </tio:accessTo>
          <xsl:apply-templates mode="in-ticket-placeholder"/>
        </tio:TicketPlaceholder>
      </gr:includes>
      <xsl:apply-templates mode="in-offering"/>
    </gr:Offering>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]" mode="in-service">
    <rdfs:label>
      <xsl:value-of select="text()"/>
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
  
  <xsl:template match="field[@name='Archived']/text" mode="in-service">
    <adhoc:serviceLifecycle rdf:resource="https://data.ox.ac.uk/id/itservices/service-lifecycle/{lower-case(.)}"/>
  </xsl:template>

  <!-- Use this field to go up and re-interpret the row in the contact of its contact information -->
  <xsl:template match="field[@name='Initial_x0020_contact_x0020_phon']" mode="in-service">
    <xsl:apply-templates select="../.." mode="service-contact"/>
  </xsl:template>
  <!-- Only create a contact agent if one of the three contact fields is filled -->
  <xsl:template match="list[@name='Service Catalogue']/rows/row" mode="service-contact">
    <xsl:if test="fields/field[@name='Initial_x0020_contact_x0020_phon' or @name='Initial_x0020_Contact_x0020_Emai' or @name='Initial_x0020_Contact_x0020_Form']/*/text()">
      <oo:contact>
        <foaf:Agent rdf:about="{$service-base-uri}service/{@id}/contact">
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
        <dcterms:subject rdf:resource="{$service-base-uri}service-activity-category/{$id}"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message>Unexpected activity category: <xsl:value-of select="text()"/></xsl:message>
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

  <xsl:template match="field[@name='Status_x0020_ID']/text" mode="in-service">
    <xsl:if test="string-length(text()) &gt; 0">
      <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/status-ox-ac-uk-service">
        <xsl:value-of select="text()"/>
      </skos:notation>
    </xsl:if>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]" mode="in-activity-category">
    <skos:prefLabel>
      <xsl:value-of select="text()"/>
    </skos:prefLabel>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_group']/lookup" mode="in-service">
    <dcterms:isPartOf rdf:resource="{$service-base-uri}service/{@id}"/>
  </xsl:template>

  <xsl:template match="field[@name='Service_x0020_group_x0020_or_x00']/text" mode="in-service">
    <xsl:for-each select="key('grouped-services', ../../../@id)">
      <dcterms:hasPart rdf:resource="{$service-base-uri}service/{@id}"/>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
