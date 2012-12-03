Autocompletion
==============

The Open Data Service supports providing autocompletion functionality on form
fields. This makes it easy for you to link your data to data held by the Open
Data Service, or pull in extra data to enrich the information provided by your
users.

The basics
----------

The main search endpoint is at `https://data.ox.ac.uk/search/
<https://data.ox.ac.uk/search/>`_. Using AJAX, one makes a request with the
following parameters:

``format``
   ``autocomplete``
``q``
   The text entered so far, followed by a ``"*"``
``type``
   Optional. Filters down to a particular class of entity (e.g.
   ``spatial-thing``, ``organization``)

With a ``q`` of ``physics*``, and a ``type`` of ``organization``, this will
return something like:

.. code-block:: javascript
   
   [{'label': 'Department of Physics',
     'value': 'http://oxpoints.oucs.ox.ac.uk/id/23232673'},
    {'label': 'Rudolf Peierls Centre for Theoretical Physics',
     'value': 'http://oxpoints.oucs.ox.ac.uk/id/23232725'},
    {'label': 'Particle Physics',
     'value': 'http://oxpoints.oucs.ox.ac.uk/id/23232664'},
    {'label': 'Atomic and Laser Physics',
     'value': 'http://oxpoints.oucs.ox.ac.uk/id/23232530'},
    {'label': 'Atmospheric Oceanic and Planetary Physics',
     'value': 'http://oxpoints.oucs.ox.ac.uk/id/23232529'},
    {'label': 'Condensed Matter Physics',
     'value': 'http://oxpoints.oucs.ox.ac.uk/id/23232567'}]

This can be fed to the `jQuery UI autocomplete plugin
<http://jqueryui.com/demos/autocomplete/>`_.

Hooking up with the autocomplete plugin
---------------------------------------



.. code-block:: javascript

	$(function() {
		$('.autocomplete').each(function(i, e) {
			e = $(e);
			var searchURL = e.attr('data-search-url') || window.searchURL;
			var h = $('<input type="hidden">').attr('name', e.attr('name')).val(e.val());
			e.attr('name', e.attr('name') + '-label').after(h);
			if (e.val()) {
				var originalVal = e.val();
				e.val("looking upâ€¦");
				$.get(searchURL, {
					q: "uri:\""+originalVal+"\"",
					format: 'autocomplete',
					type: e.attr('data-type')
				}, function(data) {
					e.val(data ? data[0].label : originalVal);
				});
			}
			e.autocomplete({
				source: function(request, callback) {
					$.get(searchURL, {
						q: request.term + '*',
						format: 'autocomplete',
						type: e.attr('data-type')
					}, callback, 'json');
				},
				minLength: 2,
				focus: function(event, ui) {
					e.val(ui.item.label);
					return false;
				},
				select: function(event, ui) {
					e.val(ui.item.label);
					h.val(ui.item.value);
					return false;
				}
			});
		});
	});