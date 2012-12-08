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
    xpath-default-namespace="https://github.com/ox-it/python-sharepoint/"
    version="2.0">
  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="service-base-uri">https://data.ox.ac.uk/id/itservices/</xsl:variable>
  <xsl:variable name="group-base-uri">https://data.ox.ac.uk/id/group/membership/</xsl:variable>
  <xsl:variable name="it-services">http://oxpoints.oucs.ox.ac.uk/id/31337175</xsl:variable>
  <xsl:variable name="university-of-oxford">http://oxpoints.oucs.ox.ac.uk/id/00000000</xsl:variable>

  <xsl:key name="user-bases" match="/site/lists/list[@name='User bases']/rows/row" use="@id"/>
  <xsl:key name="users" match="/site/users/user" use="@id"/>

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
    <rdf:RDF>
      <xsl:apply-templates/>
    </rdf:RDF>
  </xsl:template>

  <xsl:template match="*" mode="#all">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  <xsl:template match="text()|@*" mode="#all"/>
  
  <xsl:template match="list[@name='Service Catalogue']/rows">
    <gr:BusinessEntity rdf:about="{$it-services}">
      <xsl:for-each select="row">
        <gr:offers>
          <xsl:apply-templates select="."/>
        </gr:offers>
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
        <foaf:Agent rdf:about="{$service-base-uri}service/{@id}/contact">
          <xsl:apply-templates select="fields/field[*/text()]" mode="service-contact"/>
        </foaf:Agent>
      </oo:contact>
    </xsl:if>
  </xsl:template>
  <xsl:template match="field[@name='Initial_x0020_contact_x0020_phon']" mode="service-contact">
    <xsl:variable name="extension" select="text/text()"/>
    <xsl:variable name="prefix">
      <!-- From page 6 of the Internal Telephone Directory ("Extensions") -->
      <xsl:choose>
        <xsl:when test="starts-with($extension, '1')">+18656</xsl:when>
        <xsl:when test="starts-with($extension, '7')">+18652</xsl:when>
        <xsl:when test="starts-with($extension, '8')">+18652</xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$prefix">
      <v:tel>
        <v:Voice rdf:about="tel:{$prefix}{$extension}"/>
      </v:tel>
    </xsl:if>
    <adhoc:oxfordExtensionNumber>
      <xsl:value-of select="$extension"/>
    </adhoc:oxfordExtensionNumber>
  </xsl:template>
  <xsl:template match="field[@name='Initial_x0020_Contact_x0020_Emai']" mode="service-contact">
    <v:email rdf:resource="mailto:{text/text()}"/>
  </xsl:template>
  <xsl:template match="field[@name='Initial_x0020_Contact_x0020_Form']" mode="service-contact">
    <oo:contactForm rdf:resource="{url/@href}"/>
  </xsl:template>

  <xsl:template match="field[@name='Activity_x0020_category']/lookup" mode="in-service">
    <dcterms:subject rdf:resource="{$service-base-uri}activity-category/{@id}"/>
  </xsl:template>
  
  <xsl:template match="field[@name='Generic_x0020_user_x0020_bases']/lookup" mode="in-offering">
    <gr:eligibleCustomerTypes rdf:resource="{key('user-bases', @id)/fields/field[@name='URI']/text/text()}"/>
  </xsl:template>

  <xsl:template match="field[@name='Specific_x0020_user_x0020_bases']/user" mode="in-offering">
    <xsl:variable name="user" select="key('users', @id)"/>
    <xsl:if test="$user/d:ContentType = 'DomainGroup'">
      <gr:eligibleCustomerTypes rdf:resource="{$group-base-uri}{substring-after($user/d:Account, 'AD-OAK\group_')}"/>
    </xsl:if>
  </xsl:template>


  <xsl:template match="list[@name='Service activity categories']/rows">
    <skos:ConceptScheme rdf:about="{$service-base-uri}activity-category">
      <skos:prefLabel>Activity categories</skos:prefLabel>
      <dcterms:publisher rdf:resource="{$it-services}"/>
      <xsl:for-each select="row">
        <skos:topConcept>
          <xsl:apply-templates select="."/>
        </skos:topConcept>
      </xsl:for-each>
    </skos:ConceptScheme>
  </xsl:template>

  <xsl:template match="list[@name='Service activity categories']/rows/row">
    <skos:Concept rdf:about="{$service-base-uri}activity-category/{@id}">
      <xsl:apply-templates mode="in-activity-category"/>
    </skos:Concept>
  </xsl:template>

  <xsl:template match="field[@name='Title']/text[text()]" mode="in-activity-category">
    <skos:prefLabel>
      <xsl:value-of select="text()"/>
    </skos:prefLabel>
  </xsl:template>

  <xsl:template match="user">
    <xsl:if test="d:ContentType = 'DomainGroup'">
      <gr:BusinessEntityType rdf:about="{$group-base-uri}{substring-after(d:Account, 'AD-OAK\group_')}">
        <rdfs:label>
          <xsl:value-of select="substring-before(d:Name, ' Group')"/>
        </rdfs:label>
      </gr:BusinessEntityType>
    </xsl:if>
  </xsl:template>
        
</xsl:stylesheet>