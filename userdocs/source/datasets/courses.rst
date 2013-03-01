Courses
=======

.. note::

   This dataset was created as part of the `JISC course data programme
   <http://www.jisc.ac.uk/whatwedo/programmes/elearning/coursedata.aspx>`_.

The `courses dataset <https://data.ox.ac.uk/id/dataset/courses>`_ contains
metadata about graduate training opportunities from various providers within
the University. The list of systems from which course data is exposed can be
found `using this SPARQL query <https://data.ox.ac.uk/sparql/?query=SELECT+*+WHERE+{%0D%0A++%3Chttps%3A%2F%2Fdata.ox.ac.uk%2Fid%2Fdataset%2Fcourses%3E+void%3Asubset+%3Fsubset+.%0D%0A++%3Fsubset%0D%0A++++rdfs%3Alabel+%3Fname+%3B%0D%0A++++dcterms%3Apublisher%2Fdc%3Atitle+%3Fprovider%0D%0A}&format=&common_prefixes=on>`_.

Data are stored within the system as RDF, but can be requested as XCRI-CAP. All
of the :doc:`standard APIs </api/index>` are also available for use with the
courses dataset.


License
-------

All data within the courses dataset (and sub-datasets) is released under the
terms of the `Open Government License
<http://www.nationalarchives.gov.uk/doc/open-government-licence/>`_.

XCRI-CAP feeds
--------------

There are XCRI-CAP feeds for each provider, and a couple of amalgamated feeds
at https://course.data.ox.ac.uk/catalogues/.

The XCRI-CAP specification can be found at
http://www.xcri.co.uk/data-definitions-and-vocabulary-framework.html.

The simple XCRI-CAP feeds contain just one ``<provider/>`` element, to comply
with the requirements of the course data programme. In these cases the provider
is the publisher of the feed. For example, as Daisy is a system maintained by
the Social Sciences Division they are listed as its publisher, and the
University is the publisher of the amalgamated feed.

The 'full' feeds have multiple ``<provider/>`` elements, each containing the
courses offered by that provider. Unless you are constrained by the course data
programme specification, it is recommended that you use these feeds in
preference to the simple feeds.


Search API
----------

There is a simple course search available at
https://course.data.ox.ac.uk/search/. For more complicated searching, it is
recommended that you use the :ref:`elasticsearch-endpoint`.


RDF Modelling
-------------

The RDF modelling follows the structure of the XCRI-CAP XML specification. Here
are the classes:

=================== ==========================================================
Class name          Description
=================== ==========================================================
xcri:catalog        A collection of courses.
xcri:provider       An organization providing courses. You shouldn't need to
                    rely on the presence of this class, rather something is a
                    provider if it ``mlo:offers`` one or more ``xcri:course``
                    resources.
xcri:course         The "concept" of a course, divorced from the concept of an
                    instance of it being delivered.
xcri:presentation   An instance of a course being delivered as a whole unit of
                    learning. A presentation may take place over several
                    sessions.
oxcap:Session       An Oxford-specific class for a session within a
                    presentation. Not all presentations have sesion
                    information.
=================== ==========================================================

And here are the relevant predicates:

=================== ==========================================================
Predicate name      Description
=================== ==========================================================
skos:member         Used to say that a course is within a catalog, or that a
                    catalog includes all courses from another catalog. Thus,
                    to find all courses in a catalog one should use the
                    pattern
                    ``?catalog skos:member* ?course . ?course a xcri:course``.
mlo:offers          Relates a provider to a course it offers.
mlo:specifies       Relates a course to one of its presentations.
mlo:consistsOf      Relates a presentation to one of its sessions.
dcterms:title       The title of a course or presentation. Note that we use
                    the ``dcterms:`` namespace, not the ``dc:`` namespace used
                    by the XCRI-CAP XML specification.
dcterms:description The description of a course or presentation
dcterms:subject     Relates a course to a concept in some classification
                    scheme, such as the Oxford version of the Researcher
                    Development Framework, JACS, or whether the course
                    develops quantitative or qualitative research skills. For
                    more information, see :ref:`course-catagorizations` below.
=================== ==========================================================

.. _course-catagorizations:

Catagorizations
---------------

Courses are categorized — using dcterms:subject properties — in zero or more of
the schemes described below. Each is modelled using `SKOS
<http://www.w3.org/2004/02/skos/>`_, the Simple Knowledge Organization System.

Each skos:ConceptScheme has one or more ``skos:hasTopConcept`` properties,
pointing at ``skos:Concept`` resources. ``skos:Concept`` resources may have
``skos:narrower`` properties, pointing at more specific concepts. Every concept
within a scheme is linked to that scheme using a ``skos:inScheme`` property.
For more information on SKOS relations, see `§8 of the SKOS Reference
<http://www.w3.org/TR/skos-reference/#semantic-relations>`_.

Each concept has a ``skos:notation`` property containing an identifier. The
datatype of that property effectively provides a namespace for that notation
scheme. You can read more about SKOS notations in `§6 of the SKOS Reference
<http://www.w3.org/TR/skos-reference/#notations>`_.

The Oxford version Researcher Development Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Concept scheme:
  https://data.ox.ac.uk/id/ox-rdf/concept-scheme
Example concept:
  https://data.ox.ac.uk/id/ox-rdf/descriptor/LS
Notation datatype:
  https://data.ox.ac.uk/id/ox-rdf/notation

This is a simplified, aligned version of the `Researcher Development Framework
<http://www.vitae.ac.uk/researchers/428241/Researcher-Development-Framework.html>`_
maintained and controlled by `Vitae <http://www.vitae.ac.uk/>`_. It is
maintained `in GitHub
<https://github.com/ox-it/xcri-rdf/tree/master/thesauri/oxRDF>`_.

Oxford Research Methods Classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Concept scheme:
  https://data.ox.ac.uk/id/ox-rm/concept-scheme
Example concept:
  https://data.ox.ac.uk/id/ox-rm/qualitative
Notation datatype:
  https://data.ox.ac.uk/id/ox-rm/notation

This contains just two concepts, one for qualitative research methods, and one
for quantitative. It is maintained `in GitHub
<https://github.com/ox-it/xcri-rdf/tree/master/thesauri/oxRM>`_.

Joint Academic Coding System (JACS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Concept scheme:
  `http://jacs.dataincubator.org/ <https://data.ox.ac.uk/doc/?uri=http%3A%2F%2Fjacs.dataincubator.org%2F>`_
Example concept:
  `http://jacs.dataincubator.org/v144 <https://data.ox.ac.uk/doc/?uri=http%3A%2F%2Fjacs.dataincubator.org%2Fv144>`_
Notation datatype:
  `http://jacs.dataincubator.org/notation <https://data.ox.ac.uk/doc/?uri=http%3A%2F%2Fjacs.dataincubator.org%2Fnotation>`_

The `JACS article on Wikipedia
<http://en.wikipedia.org/wiki/Joint_Academic_Classification_of_Subjects>`_
provides plentiful information about JACS.

Since it is no longer hosted by the `Data Incubator
<http://dataincubator.org/>`_, we create an RDF version from the `HESA JACS CSV
file <http://www.hesa.ac.uk/dox/jacs/JACS.csv>`_, which is `stored in GitHub
<https://github.com/ox-it/xcri-rdf/tree/master/thesauri/jacs>`_.

The Researcher Development Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Concept scheme:
  `http://id.vitae.ac.uk/rdf/concept-scheme <https://data.ox.ac.uk/doc/?uri=http%3A%2F%2Fid.vitae.ac.uk%2Frdf%2Fconcept-scheme>`_
Example concept:
  `http://id.vitae.ac.uk/rdf/descriptor/A.2.2.2 <https://data.ox.ac.uk/doc/?uri=http%3A%2F%2Fid.vitae.ac.uk%2Frdf%2Fdescriptor%2FA.2.2.2>`_
Notation datatype:
  http://id.vitae.ac.uk/rdf/notation

We maintain an RDF version of `Vitae`_'s `Researcher Development Framework`_,
generated from a `spreadsheet in GitHub
<https://github.com/ox-it/xcri-rdf/tree/master/thesauri/vitaeRDF>`_.

Although not used to directly annotate courses, we have aligned it with the
Oxford simplified version, so it can still be used in queries.


Example resources
-----------------

* `Course catalogue for the University of Oxford <https://course.data.ox.ac.uk/id/catalogue>`_ (a catalog, which contains other catalogs)
* `Archaeology in Practice <https://course.data.ox.ac.uk/id/continuing-education/course/V400-201>`_ (a Continuing Education course)
* `Archaeology in Practice <https://course.data.ox.ac.uk/id/continuing-education/presentation/O12P495AHV>`_ (an online presentation)
* `Department of Computer Science <https://data.ox.ac.uk/doc:oxpoints/23232561>`_ (a provider, with courses managed by Daisy)
* `Categories, Proofs and Processes <https://course.data.ox.ac.uk/id/daisy/course/6200>`_ (a course with various categorisations)

