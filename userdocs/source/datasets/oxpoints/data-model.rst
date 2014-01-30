The OxPoints data model
=======================

.. note::

   The `OxPoints ontology <https://data.ox.ac.uk/doc/?uri=http%3A%2F%2Fns.ox.ac.uk%2Fnamespace%2Foxpoints%2F2009%2F02%2Fowl%23>`_ defines OxPoints-specific terms.

OxPoints contains two broad classes of things:

 * organizations (colleges, departments, faculties, etc.)
 * places (sites, buildings, rooms, etc.)


Organizations
-------------

Our definition of an organization is taken from the `W3C Organization Ontology
<http://www.w3.org/TR/vocab-org/#class-organization>`_:

    Represents a collection of people organized together into a community or
    other social, commercial or political structure. The group has some common
    purpose or reason for existence which goes beyond the set of people belonging
    to it and can act as an Agent. Organizations are often decomposable into
    hierarchical structures. 

.. note::

   Because organizations are groups they don't have any physical manifestion
   (e.g., they don't have spatial co-ordinates). In general parlance we often
   conflate a department and the building it occupies ("Where is the Department of
   Statistics?"), relying on context to make it clear that we're talking about a
   building. In OxPoints, the distinction between organization and the places it
   occupies is made explicit. You'll want to use the ``org:hasPrimarySite`` and
   ``org:hasSite`` relationships to go from an organization to the places it
   occupies.

Organizations can have the following attributes:

 * addresses (specifically, a postal address — this should not be presented to a user when they want to visit one of the organization's buildings)
 * social media account names
 * telephone and fax numbers
 * various identifiers, both internal to the University, and externally assigned

Organizations are arranged into a hierarchy using the ``org:subOrganizationOf``
relation. It's thus possible to find all units of the University by traversing
the tree of sub-organization relationships.


Places
------

Places are extents in physical space. They may be disjoint (e.g. a site divided
by a road).

A place exists in OxPoints if it's worthwhile to be able to refer to it. Thus,
"the bit of the Manor Road Building occupied by the Oxford Institute of Aging"
is a reasonable definition of a place that might exist in OxPoints.

Like organizations, places are arranged into a tree, this time using the
``spatialrelations:within`` relationship.

.. note ::

   At the moment, OxPoints does not support a place being directly contained by more than one thing. Support for this is planned, which will enable us to model the following cases:

   * a college room being contained by both a staircase and a floor
   * a space occupied by a library that spans more than one floor
   * spaces whose purpose is to provide a logical grouping of other spaces
