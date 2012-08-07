<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oo="http://purl.org/openorg/"
    xmlns:cerif="http://spi-fm.uca.es/neologism/cerif#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:vcard="http://www.w3.org/2006/vcard/ns#"
    xmlns:spatialrelations="http://data.ordnancesurvey.co.uk/ontology/spatialrelations/"
    xmlns:srx="http://www.w3.org/2005/sparql-results#"
    xmlns:gr="http://purl.org/goodrelations/v1#"
    xmlns:ex="http://www.example.org/"
    xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:org="http://www.w3.org/ns/org#"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:tio="http://purl.org/tio/ns#"
    xmlns:adhoc="http://vocab.ox.ac.uk/ad-hoc-data-ox/"
  >
  <xsl:import href="common.xsl"/>

  <!-- SKOS Concept Scheme generation -->
  <xsl:template match="/">
    <xsl:variable name="items">
      <xsl:for-each-group select="//tei:table[1]/tei:row[position() &gt; 1]" group-by="position()">
        <xsl:call-template name="preprocess"/>
      </xsl:for-each-group>
    </xsl:variable>
    <rdf:RDF>
      <skos:ConceptScheme rdf:about="https://data.ox.ac.uk/id/equipment-category">
        <skos:prefLabel>Taxonomy for research facilities and equipment at the University of Oxford</skos:prefLabel>
        <dcterms:publisher rdf:resource="http://oxpoints.oucs.ox.ac.uk/id/23233536"/>
        <xsl:for-each-group select="$items/item" group-by="ex:slugify(category)">
          <skos:hasTopConcept>
            <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-category/{ex:slugify(category)}">
              <skos:prefLabel>
                <xsl:value-of select="category"/>
              </skos:prefLabel>
              <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/equipment-category">
                <xsl:value-of select="ex:slugify(category)"/>
              </skos:notation>
              <xsl:for-each-group select="current-group()" group-by="ex:slugify(subcategory)">
                <skos:narrower>
                  <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-category/{ex:slugify(category)}/{ex:slugify(subcategory)}">
                    <skos:prefLabel>
                      <xsl:value-of select="subcategory"/>
                    </skos:prefLabel>
                    <skos:notation rdf:datatype="https://data.ox.ac.uk/id/notation/equipment-category">
                      <xsl:value-of select="concat(ex:slugify(category), '/', ex:slugify(subcategory))"/>
                    </skos:notation>
                  </skos:Concept>
                </skos:narrower>
              </xsl:for-each-group>

            </skos:Concept>
          </skos:hasTopConcept>
        </xsl:for-each-group>

      </skos:ConceptScheme>
      <skos:ConceptScheme rdf:about="https://data.ox.ac.uk/id/equipment-shareability">
        <skos:prefLabel>Taxonomy of equipment shareability statuses</skos:prefLabel>
        <dcterms:publisher rdf:resource="http://oxpoints.oucs.ox.ac.uk/id/23233536"/>
        <skos:hasTopConcept>
          <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-shareability/yes">
            <skos:prefLabel>yes</skos:prefLabel>
            <skos:definition>The item will likely be available for use by members of the University of Oxford.</skos:definition>
          </skos:Concept>
        </skos:hasTopConcept>
        <skos:hasTopConcept>
          <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-shareability/contact">
            <skos:prefLabel>contact for details</skos:prefLabel>
            <skos:definition>No information is held about whether the item is able to be shared. Please contact for more information.</skos:definition>
          </skos:Concept>
        </skos:hasTopConcept>
        <skos:hasTopConcept>
          <skos:Concept rdf:about="https://data.ox.ac.uk/id/equipment-shareability/no">
            <skos:prefLabel>contact for details</skos:prefLabel>
            <skos:definition>It is unlikely that the item is available for re-use by others.</skos:definition>
          </skos:Concept>
        </skos:hasTopConcept>
      </skos:ConceptScheme>
    </rdf:RDF>
  </xsl:template>
</xsl:stylesheet>
