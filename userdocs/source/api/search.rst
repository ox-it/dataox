Search
======

The Open Data Service provides a search interface over various types of
entities in the :term:`triple store`. Behind the scenes, search is provided by
an `ElasticSearch <http://www.elasticsearch.org/>`_ instance.

Indexed entities
----------------

The search service only indexes certain classes of thing. These are:

* Organizations (including colleges and units) (``organization``)
* Places (including buildings, sites and rooms) (``spatial-thing``)
* Equipment (``equipment``)
* Vacancies (``vacancy``)
* Courses (``course``)

The identifier in brackets can be used to :ref:`filter results
<search-filtering>`.

The indexes are built from SPARQL queries whose results are converted to JSON.
We've made some judgement calls on what should and shouldn't be indexed, and
whether any of those fields should be weighted. If you need something added —
either to an existing index, or a completely new index — :doc:`contact us to
request a change </contact>`.


Simple search endpoint
----------------------

The simple search endpoint is at https://data.ox.ac.uk/search/, and implements
the `OpenSearch <http://www.opensearch.org/>`_ specification.

It minimally takes a ``q`` parameter, for providing a query in the `Lucene
query syntax
<http://lucene.apache.org/core/old_versioned_docs/versions/2_9_1/queryparsersyntax.html>`_.
The query syntax is rather expressive, so it's well worth familiarising
yourself with it.

Pagination is handled using the ``page`` and ``page_size`` parameters.

The endpoint supports HTML, OpenSearch Atom, JSON and JSONP serializations. You
can express a preference using :term:`content negotiation`, or a ``format``
query parameter. The format identifiers are ``html``, ``atom``, ``json``, and
``js``, respectively.

By default, the endpoint will search for the conjunction of all search terms,
so a search for 'Keble College' will not return things that only mention
'Keble' and not 'College'. To change this behaviour, you can specifify a
``default_operator=or`` parameter.


.. _search-filtering:

Filtering
~~~~~~~~~

You can restrict results to a particular type of thing using the ``type``
parameter. For example, https://data.ox.ac.uk/search/?q=computing&type=vacancy
will search for computing vacancies.

Examples
~~~~~~~~

Here are some examples:

* https://data.ox.ac.uk/search/?q=merton&type=spatial-thing (places related to Merton)
* https://data.ox.ac.uk/search/?q=Wolfson+Building,+Parks+Road,+Oxford,+OX1+3QD&default_operator=or&type=organization (organizations relevant to (e.g. occupying) the Wolfson Building; i.e. the Department of Computer Science)


ElasticSearch endpoint
----------------------

The Open Data Service exposes the raw ElasticSearch query endpoint for stores,
linked from https://admin.data.ox.ac.uk/stores/. This endpoint allows you to
query using a very expressive JSON-based `DSL
<http://en.wikipedia.org/wiki/Domain-specific_language>`_, and returns results
as JSON.

You can read more about the query language in the `ElasticSearch documentation
<http://www.elasticsearch.org/guide/reference/api/search/>`_.
