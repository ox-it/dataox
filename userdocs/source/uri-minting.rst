Minting URIs for the Open Data Service
======================================

Everything that the Open Data Service knows about is identified with a
:term:`Uniform Resource Identifier (URI) <URI>`.

Where these don't already exist, we need to specify schemes for creating them.

General principles
------------------

For data controlled at the institutional level, we should use URIs in the
``https://data.ox.ac.uk/id/`` namespace. In the simple case, URIs should take
the form ``https://data.ox.ac.uk/id/[type]/[identifier]``.

Where possible, the identifier should be canonical and controlled by an
institutional data provider. This identifier should be applicable to all
instances of a particular thing in the University. For example, we wouldn't
use an SSO username to identify people, because not everyone relevant to the
University has one.

Where there are competing identifier schemes for a particular type of thing:

* if the identifier schemes are used for disjoint subsets, then we can use
  them, but encode the identifier scheme in the URI. For example, courses
  managed by `Daisy <https://daisy.socsci.ox.ac.uk/>`_ have a `daisy`
  component in their URI.
* if multiple schemes can apply to a given individual, it may be necessary
  to create a new identifier scheme for use in the URI.

The ``[type]`` path component should be a :term:`slugified <slugification>`
string that identifies the class of things being described. However:

* steer away from type names that won't necessarily be constant for the life
  of a thing. For example ``pph`` (Permanent Private Hall) would be bad as
  PPHs sometimes get "promoted" to colleges (e.g. St Edmund Hall).
* Where types can be split into sub-partitions, consider using more-specific
  type identifiers. For example, ``course`` would be vague if:

  #. you plan to describe both undergraduate and skills courses
  #. those courses are managed entirely separately, and would never be managed
     using the same system.

  In this case, use something like ``degree-programme`` and ``skills-course``.

Existing URI namespaces
-----------------------

This is an incomplete list of URI namespaces are already in use within the Open
Data Service.

``https://data.ox.ac.uk/id/graph/[path]``
    RDF graphs (of type ``sd:Graph``). ``[path]`` is usually structured using
    the source name, and then another component to signify a partition or
    whether it's a dataset, or dataset metadata. Examples of ``[path]``
    include ``oxpoints/data``, ``oxpoints/metadata``, ``vacancies/archive`` and
    ``vacancies/current``. A list of all current graph URIs in use can be seen
    at https://backstage.data.ox.ac.uk/stores/public/data/.

``https://data.ox.ac.uk/id/dataset/[path]``
    Datasets, VoID or otherwise. Each should be a ``dcat:Dataset`` instance.
    Generally ``[path]`` will be a single component, but where datasets are
    composed of sub-datasets, it's generally a good idea to create a hierarchy.
    Examples include ``catalogue``, ``oxpoints``, ``courses``, and
    ``courses/medsci``.

``http://oxpoints.oucs.ox.ac.uk/id/[id]``
    Entities in OxPoints, e.g. departments, buildings, committees. IDs are
    arbitrarily-assigned eight-digit strings.

``https://data.ox.ac.uk/id/itservices/service/[id]``
    Services offered by IT Services. IDs are SharePoint row IDs from the
    Service Catalogue list.

``https://data.ox.ac.uk/id/qb-data-structure/[id]``
    Data structures for the `Data Cube vocabulary
    <http://www.w3.org/TR/vocab-data-cube/>`_. Each should be a
    ``qb:DataStructureDefinition``, with sub-resources (measures, slices, etc)
    using URIs below that of the data structure definition resource.
