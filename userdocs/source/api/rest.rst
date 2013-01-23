RESTful API
===========

All pages on the site are available in a variety of formats, either through
content negotiation or a query parameter. Any :term:`URI` can be looked up
using an endpoint, which will return data about the resource identified by that
URI.


URI look-up endpoint
--------------------

The endpoint is at https://data.ox.ac.uk/doc/?uri=; simply append the
URL-encoded form of the URI you want to look up. The site may redirect you to
another page if there is a shorter URL for the descriptive page.

For example, http://oxpoints.oucs.ox.ac.uk/id/00000000 is the identifier for
the University of Oxford. By appending it we get
https://data.ox.ac.uk/doc/?uri=http%3A//oxpoints.oucs.ox.ac.uk/id/00000000,
which redirects to https://data.ox.ac.uk/doc:oxpoints/00000000. This page then
provides information about the University.

To follow links in returned RDF data, you may either resolve the URI directly
(to see what the original source said about that thing), or use the URI look-up
endpoint to discover information held by the Open Data Service.


Content negotiation
-------------------

Each page supports :term:`content negotiation` on the ``Accept`` header,
allowing you to provide a list of preferred formats for the response. For
example, an ``Accept`` header of ``application/rdf+xml, text/turtle;q=0.9,
text/html;q=0.8`` would tell the server that you'd like (in decreasing order of
precedence) :term:`RDF/XML`, :term:`turtle`, and HTML.

It's also possible to specify the required format with a format extension
(where the URL doesn't end in a slash, or have a query string), or with a
``format`` query parameter (in all other cases). This should not be used in the
general case, but is useful when using tools that don't support setting the
``Accept`` header. For example, https://data.ox.ac.uk/doc:oxpoints/00000000.rdf
is information about the University of Oxford serialized as RDF/XML, and
https://data.ox.ac.uk/datasets/?format=ttl is a Turtle representation of the
dataset catalogue.

