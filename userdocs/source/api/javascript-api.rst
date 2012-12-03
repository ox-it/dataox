JavaScript API
==============

The JavaScript API provides simple support for:

* Displaying maps
* :doc:`SPARQL queries </api/sparql>`
* :doc:`Auto-completion </api/autocomplete>`

.. And not yet: * :doc:`Searching </api/search>`

The API uses annotations on HTML elements to work out what to do, meaning that
for simple cases you don't need to write any JavaScript of your own. 

.. note::

   To show you what the API's capable of, we've built `a demonstation page
   <../_static/examples/api.html>`_.

Getting started
---------------

The API can be used by including the following in your webpage:

.. code-block :: html

   <script language="text/javascript" src="//static.data.ox.ac.uk/js/jquery-1.7.2.min.js"></script>
   <script language="text/javascript" src="//static.data.ox.ac.uk/jquery-ui/js/jquery-ui-1.8.22.custom.min.js"></script>
   <script language="text/javascript" src="//static.data.ox.ac.uk/OpenLayers-2.12/OpenLayers.js"></script>
   <script language="text/javascript" src="//static.data.ox.ac.uk/api-1.0.js"></script>

.. note::

   The script locations (starting with ``//``) are `protocol-relative
   <http://paulirish.com/2010/the-protocol-relative-url/>`_, and will be
   interpreted as ``http`` or ``https`` depending on how the web page was
   served.

If you don't intend to use the auto-completion you can omit ``jquery-ui``, and
if you're not going to be displaying maps, you can omit ``OpenLayers``. If
you'd prefer to use another version of jQuery or jQuery UI you should be aware
that we can't guarantee compatibility.

Displaying maps
---------------

Without JavaScript
~~~~~~~~~~~~~~~~~~

Let's start with an example:

.. code-block:: html

   <div class="dataox-map" data-lon="-1.259579" data-lat="51.76051" style="width:300px; height:300px"></div>

The map defaults to a zoom level of 14, which makes sense for displaying
maps in the context of Oxford. If you want to use a `different zoom
<http://wiki.openstreetmap.org/wiki/Zoom_levels>`_, use a ``data-zoom``
attribute; lower numbers are zoomed out, and higher numbers (up to 18) are
zoomed in.

With JavaScript
~~~~~~~~~~~~~~~

Here's another example:

.. code-block:: javascript

   dataox.map("element-id", {
       lon: -1.259579,
       lat: 51.76051,
       zoom: 13
   });

The first parameter to ``dataox.map()`` can be either an element ID, an HTML
DOM element, or a jQuery object. The second parameter is a JavaScript object
with ``lon`` and ``lat`` attributes, and optionally a ``zoom`` parameter.

Using OxPoints IDs
~~~~~~~~~~~~~~~~~~

If you know the OxPoints IDs of some places you want to show, you can specify
them as an attribute, and the API will look them up:

.. code-block:: html

   <div class="dataox-map" data-oxpoints-ids="23232373 40002001" style="width:300px; height:300px"></div>


Performing SPARQL queries
-------------------------

The API provides a small wrapper around jQuery for performing SPARQL queries
which can be invoked as ``dataox.sparql``:

.. function:: dataox.sparql(query, callback)

Here's an example, using data from the :doc:`vacancy dataset </datasets/vacancy>`:

.. code-block:: javascript

   // Here's a query for getting all current vacancies for IT Services or any
   // of its sub-units.
   var query = ["SELECT ?vacancy ?label ?homepage WHERE {",
                "  ?vacancy a vacancy:Vacancy ;",
                "    oo:organizationPart/^org:subOrganizationOf* <http://oxpoints.oucs.ox.ac.uk/id/31337175> ;",
                "    vacancy:applicationOpeningDate ?opening ;",
                "    vacancy:applicationClosingDate ?closing ;",
                "    rdfs:label ?label ;",
                "    foaf:homepage ?homepage",
                "  FILTER (?opening < now() && now() < ?closing)",
                "}"].join("\n");

   dataox.sparql(query, function(data) {
       // Find the UL which will contain the vacancy information
       var ul = $('ul#vacancies');
       
       // Loop through the bindings that were returned.
       for (var i=0; i<data.results.bindings.length; i++) {
           var binding = data.results.bindings[i];
           ul.append($('<li/>').append($('<a/>').attr('href', binding.homepage.value)
                                                .text(binding.label.value)));
       }
   }

``dataox.sparql()`` takes a :term:`SPARQL` query as its first argument, and a
callback as its second. The callback will receive a JavaScript object
containing the results as `SPARQL Results JSON
<http://www.w3.org/TR/rdf-sparql-json-res/>`_.

For convenience, this function also sends the ``common_prefixes`` parameter,
which means you don't need to specify prefixes for a lot of prefixes.
