How do I…
=========

Here are some common use-cases, and how to satisfy them using OxPoints
data.

… direct a user to the reception for a department?
--------------------------------------------------


… show where a unit is?
-----------------------


… generate an address for a room?
---------------------------------


… show the location of a room on a map?
---------------------------------------

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

