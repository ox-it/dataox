Glossary
========

.. glossary ::
   :sorted:
   
   Fuseki
      Part of the `Apache Jena project <http://jena.apache.org/>`_, Fuseki
      is Free Software bringing together a :term:`triple store`, a
      :term:`SPARQL` implementation, and the `graph store HTTP protocol
      <http://www.w3.org/TR/sparql11-http-rdf-update/>`_. The Open Data
      Service uses Fuseki for storing and mediating access to the available
      data.

   linked data
      A pattern for publishing data on the web using URIs as identifiers, so
      that it can be interlinked and thus gain greater utility by becoming
      part of the *web of data* (by analogy to the human-readable *web of
      documents*). See `the Wikipedia article
      <http://en.wikipedia.org/wiki/Linked_data>`_ for more information.
      
      If you're just getting started with linked data, the Open Data Team at
      Southampton have put together this `useful guide for beginners
      <http://openorg.ecs.soton.ac.uk/wiki/Linked_Data_Basics_for_Techies>`_.

   open data stars
      The stars represent the extent to which a dataset is part of the linked
      open data web. These were the definitions used by Tim Berners-Lee during
      his `Gov 2.0 talk <http://www.youtube.com/watch?v=ga1aSJXCFe0>`_ in 2010,
      and have since become widely accepted as an ideal to work towards.

      .. raw:: html

         <table>
           <tbody>
             <tr>
               <td><img src="https://static.data.ox.ac.uk/desc/stars/data-badge-0.png" alt="0 stars"/></td>
               <td>Data available, but not openly licensed</td>
             </tr>
             <tr>
               <td><img src="https://static.data.ox.ac.uk/desc/stars/data-badge-1.png" alt="1 star"/></td>
               <td>Put your data on the web with an open license (in any format)</td>
             </tr>
             <tr>
               <td><img src="https://static.data.ox.ac.uk/desc/stars/data-badge-2.png" alt="2 stars"/></td>
               <td>Make it available in a machine readable format (i.e. no image scans!)</td>
             </tr>
             <tr>
               <td><img src="https://static.data.ox.ac.uk/desc/stars/data-badge-3.png" alt="3 stars"/></td>
               <td>Use a open, standard format (eg JSON)</td>
             </tr>
             <tr>
               <td><img src="https://static.data.ox.ac.uk/desc/stars/data-badge-4.png" alt="4 stars"/></td>
               <td>Use an open, linked data format (URIs for everything so people can point to your data)</td>
             </tr>
             <tr>
               <td><img src="https://static.data.ox.ac.uk/desc/stars/data-badge-5.png" alt="5 stars"/></td>
               <td>Link your data to other people’s data</td>
             </tr>
           </tbody>
         </table>

   RDF
      See :term:`Resource Description Framework`.

   RDF/XML
      A serialization of RDF into XML. Generally not considered pretty, but
      useful when creating RDF using XML tools. For more information, see
      `this explanation of it's "stripedness" <http://www.w3.org/2001/10/stripes/>`_
      and the `format specification <http://www.w3.org/TR/REC-rdf-syntax/>`_.
      
      Examples of RDF/XML can be found `here <http://data.ox.ac.uk/doc:oxpoints/31337175.rdf>`_
      and `here <http://data.ox.ac.uk/datasets/?format=rdf>`_.

   RDF serialization
      As RDF is just a data model, it doesn't have any one true concrete
      syntax. RDF triple serializations include:
      
      * :term:`RDF/XML`
      * :term:`Turtle`
      * :term:`N-Triples`
      * :term:`RDF/JSON`
   
   Resource Description Framework
      The Resource Description Framework (RDF) is a metadata data model based
      around *subject object predicate* :term:`triples <triple>`. RDF is not
      tied to representing any particular type of information, leading to an
      information infrastructure that works for just about anything.
      
      RDF is generally queried using :term:`SPARQL`. You can read more about
      RDF at the `W3C <http://www.w3.org/RDF/>`_ and
      `Wikipedia <http://en.wikipedia.org/wiki/Resource_Description_Framework>`_.
   
   SPARQL
      A query language for RDF databases. SPARQL queries can return table-like
      results (like SQL ``SELECT`` queries), or :term:`RDF <Resource Description Framework>`.
      
      Cambridge Semantics' `SPARQL by Example
      <http://www.cambridgesemantics.com/2008/09/sparql-by-example/>`_ provides
      a good introduction to the language. `answers.semantic.web
      <http://answers.semanticweb.com/>`_ is also a good resource if you get
      stuck.
      
      The Open Data Service supports all of
      `SPARQL 1.1 <http://www.w3.org/TR/sparql11-query/>`_ through `Jena ARQ
      <http://jena.apache.org/documentation/query/index.html>`_.

   triple
      An atom of information in `RDF <Resource Description Framework>`. A
      triple consists of a subject, predicate and object, such as "Alice (S)
      knows (P) Bob (O)". These units of information are then composed to
      produce 

   triple store
      A triple store is a database for storing RDF. See the `Wikipedia article
      <http://en.wikipedia.org/wiki/Triplestore>`_ for more information.

   Turtle
      An :term:`RDF serialization`, 

   vocabulary
      A set of :term:`URI` terms that have a commonly-understood interpretation
      and so can be used to describe things in RDF. A vocabulary generally
      has one particular focus, e.g. describing organisations, relationships,
      or offers to sell products. There are sites such as `Schemapedia
      <http://schemapedia.com/>`_ and `prefix.cc <http://prefix.cc/>`_ which
      help with finding vocabularies.