How do I…
=========

Here are some common use-cases, and how to satisfy them using OxPoints
data.

… direct a user to the reception for a department?
--------------------------------------------------

Remember that departments don't have locations. First, you'll need to find a place occupied by the department, and then find the reception for that.

A unit may occupy more than one place. If in doubt, give the user the option to choose the place they want to visit. A unit will normally have a primary place (expressed using the ``org:hasPrimarySite`` relationship), to which you may wish to give more weight. Where an organization doesn't have any occupied places, you'll want to find a parent organization that does by traversing ``org:isSubOrganizationOf`` relationships.

So, once you've found a place, you'll want to find out where to direct users so they can be received. For this purpose, some places have an ``oxp:reception`` relationship to another place. If the place doesn't have an associated reception, the best you can do is direct the user to the place itself.

Here are some examples of places where a reception is made explicit:

* A college's primary place is a site or building with the same name as the
  college itself. That site will contain a building or space with a name like
  'Lodge'.  There will be a ``oxp:reception`` relationship between the site and
  the lodge.  Thus, you can always find the main lodge for a college by following
  the property path ``org:hasPrimarySite/oxp:reception``
* Some buildings don't have receptions of their own, and visitors should be
  directed to a reception in another building, from where they will be collected
  or given further instructions. In this case, don't assume that the building
  contains its reception.

Once you've found a reception, you'll need to :ref:`find some co-ordinates <find-location-of-place>`.


… show where a unit is?
-----------------------


… generate an address for a room?
---------------------------------


.. _find-location-of-place:

… show the location of a place on a map?
----------------------------------------

Places in OxPoints can be annotated with a latitude or longitude. However, not everything has co-ordinates — it doesn't make sense to try to add co-ordinates for every room in a building — and so it's necessary to be able to infer a location for a place.

For any place (not just a room) you should first check whether it has co-ordinates. If not, find its containing place (using ``spatialrelations:within``) and see if that has co-ordinates. You may need to follow the containment links multiple times before you find a place with co-ordinates. Co-ordinates are stored using the ``geo:lat`` and ``geo:long`` properties.

If you're attempting this using SPARQL, you'll want to think of it as "find the first containing place with co-ordinates such that there isn't an intervening place that also has co-ordiantes". This can be expressed as:

.. code-block:: sparql

   SELECT ?place ?lat ?long WHERE {
       ?place a oxp:Room .
       OPTIONAL {
           ?place spatialrelations:within* ?container .
           ?container geo:lat ?lat ; geo:long ?long .
           # This next bit excludes containers where there's something
           # between ?place and ?container that also has co-ordinates.
           NOT EXISTS {
               ?place spatialrelations:within* ?intermediate .
               ?intermediate spatialrelations:within+ ?container ;
                   geo:lat ?intermediate_lat ;
                   geo:long ?intermediate_long
           }
       }
   }

… present a list of units or colleges in a sensible order?
----------------------------------------------------------

OxPoints has a number of types of names that can be applied to organizations and places.

The two you'll want to use are ``skos:prefLabel`` and ``ov:sortLabel``. If something should be sorted differently to its lexical label, it should have a sort label which should be used instead.

Examples where this might be the case include:

* colleges like "St John's College" should be displayed with the "St" expanded to "Saint". In this case the sort label is "Saint John's College", and it sorts above "Somerville College".
* units whose name begins with "Oxford" generally have a sort label with the Oxford moved to the end after a comma. For example "Oxford University Development Office" has a sort label of "Development Office, Oxford University"
* units whose name begins with "Department of" or "Faculty of" have this moved to the end as well. Examples include "Zoology, Department of" and "Theology, Faculty of"

You can see `the current list of sort labels <https://data.ox.ac.uk/sparql/?query=SELECT+*+WHERE+{%0D%0A%3Forganization+skos%3AprefLabel+%3FprefLabel+%3B+ov%3AsortLabel+%3FsortLabel%0D%0A}&format=&common_prefixes=on>`_.

