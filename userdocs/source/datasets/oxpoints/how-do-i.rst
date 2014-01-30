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


… present a list of units or colleges in a sensible order?
----------------------------------------------------------

OxPoints has a number of types of names that can be applied to organizations and places.

The two you'll want to use are ``skos:prefLabel`` and ``ov:sortLabel``. If something should be sorted differently to its lexical label, it should have a sort label which should be used instead.

Examples where this might be the case include:

 * colleges like "St John's College" should be displayed with the "St" expanded to "Saint". In this case the sort label is "Saint John's College", and it sorts above "Somerville College".
 * units whose name begins with "Oxford" generally have a sort label with the Oxford moved to the end after a comma. For example "Oxford University Development Office" has a sort label of "Development Office, Oxford University"
 * units whose name begins with "Department of" or "Faculty of" have this moved to the end as well. Examples include "Zoology, Department of" and "Theology, Faculty of"

You can see `the current list of sort labels <https://data.ox.ac.uk/sparql/?query=SELECT+*+WHERE+{%0D%0A%3Forganization+skos%3AprefLabel+%3FprefLabel+%3B+ov%3AsortLabel+%3FsortLabel%0D%0A}&format=&common_prefixes=on>`_.

