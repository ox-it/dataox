(function() {
	if (window.dataox == undefined)
		window.dataox = {};
	
	$.extend(window.dataox, {
		staticURL: "//static.data.ox.ac.uk/",
		sparqlURL: "//data.ox.ac.uk/sparql/",
		searchURL: "//data.ox.ac.uk/search/",
		getElement: function(e) {
			if (typeof e == "string")
				return $(getElementById(e));
			if (typeof HTMLElement == "object" ? e instanceof HTMLElement : typeof e == "object" && e.nodeType == 1)
				return $(e);
			return e;
		},
		generatedIdIndex: 0,
		generateId: function() {
			return 'dataox-element-' + window.dataox.generatedIdIndex++;
		},
		// Autocomplete. See https://data.ox.ac.uk/docs/api/autocomplete.html
		autocomplete: function(e, searchURL) {

			e = window.dataox.getElement(e); // get the jQuery-wrapped version
			var obj = e.get(0);              // and the original DOM object

			searchURL = searchURL
			         || e.attr('data-dataox-search-url')
			         || $('body').attr('data-dataox-search-url')
			         || window.dataox.searchURL;
			
			// build the default params for AJAX calls
			var defaultParams = {format: 'autocomplete'};
			for (var i = 0; i < obj.attributes.length; i++) {
				var attribute = obj.attributes[i];
				if (attribute.name.slice(0, 18) == 'data-autocomplete-')
					defaultParams[attribute.name.slice(18)] = attribute.value;
			}

			var h = $('<input type="hidden">').attr('name', e.attr('name')).val(e.val());
			e.attr('name', e.attr('name') + '-label').after(h);
			if (e.val()) {
				var originalVal = e.val();
				e.val("looking up…");
				$.get(searchURL, $.extend({}, defaultParams, {
					q: "uri:\""+originalVal+"\""
				}), function(data) {
					e.val(data ? data[0].label : originalVal);
				});
			}
			e.autocomplete({
				source: function(request, callback) {
					$.get(searchURL, $.extend({}, defaultParams, {
						q: request.term + '*'
					}), callback, 'json');
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
		},
		lonLat: function(map, lon, lat) {
			return new OpenLayers.LonLat(longitude, latitude)
				.transform(new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
				           map.getProjectionObject());
		},
		
		map: function(e, lon, lat, zoom, label) {
			e = window.dataox.getElement(e);
			var domElement = e.get(0);
			if (!domElement.id)
				domElement.id = window.dataox.generateId();
		
			var map = new OpenLayers.Map(domElement.id, { controls: [] });
			map.addLayer(new OpenLayers.Layer.OSM());
			map.addControl(new OpenLayers.Control.Navigation());

			var lonLat = window.lonLat(map,
				lon || e.attr('data-lon'),
				lat || e.attr('data-lat'));
			zoom = zoom | e.attr('data-zoom');
		 
			var markers = new OpenLayers.Layer.Markers( "Markers" );
			map.addLayer(markers);
		 
			var size = new OpenLayers.Size(21,25);
			var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
			var icon = new OpenLayers.Icon(window.dataox.staticURL + 'marker.png', size, offset);
			markers.addMarker(new OpenLayers.Marker(lonLat, icon));
		 
			map.setCenter (lonLat, zoom);
		},
		supportsCORS: ('withCredentials' in new XMLHttpRequest()),
		sparql: function(query, callback) {
			$.ajax({
				url: $('body').attr('dataox-sparql-url') || window.dataox.searchURL,
				type: "GET",
				data: { 
					query: query,
					format: window.dataox.supportsCORS ? "srj" : "srjp",
					common_prefixes: "on"
				},
				dataType: window.dataox.supportsCORS ? "json" : "jsonp",
				success: callback
			});
		}		
	});
})();

$(function() {
	$('.dataox-autocomplete').each(function(i, e) { dataox.autocomplete(e); });
	$('.dataox-map').each(function(i, e) { dataox.map(e); });
});