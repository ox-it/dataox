$(function() {
	if (window.dataox == undefined)
		window.dataox = {};
	
	$.extend(window.dataox, {
		staticURL: $('body').attr('data-dataox-static-url') ||"//static.data.ox.ac.uk/",
		sparqlURL: $('body').attr('data-dataox-sparql-url') ||"//data.ox.ac.uk/sparql/",
		searchURL: $('body').attr('data-dataox-search-url') || "//data.ox.ac.uk/search/",
		uriLookupURL: $('body').attr('data-dataox-uri-lookup-url') || "//data.ox.ac.uk/doc/",
		defaultZoom: 14,
		osmTiles: '//static.data.ox.ac.uk/osm-tiles/${z}/${x}/${y}.png',
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
			return new OpenLayers.LonLat(lon, lat)
				.transform(new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
				           map.getProjectionObject());
		},
		// Maps. https://data.ox.ac.uk/docs/api/maps.html
		map: function(e, options) {
			options = options || {};
			e = window.dataox.getElement(e);
			var domElement = e.get(0);
			if (!domElement.id)
				domElement.id = window.dataox.generateId();
		
			var map = new OpenLayers.Map(domElement.id, { controls: [] });
			map.addLayer(new OpenLayers.Layer.OSM("OpenStreetMap", window.dataox.osmTiles));
			map.addControl(new OpenLayers.Control.Navigation());

			var markers = new OpenLayers.Layer.Markers( "Markers" );
			map.addLayer(markers);

			var lon = options.lon || e.attr('data-lon');
			var lat = options.lon || e.attr('data-lat');
			var oxpointsID = options.oxpointsID || e.attr('data-oxpoints-id');
			var uri = options.uri || e.attr('data-uri');
			var zoom = options.zoom || e.attr('data-zoom') || window.dataox.defaultZoom;
			if (!uri && oxpointsID) uri = "http://oxpoints.oucs.ox.ac.uk/id/" + oxpointsID;
			if (uri) throw new Error("maps with uri lookup not yet supported.");

			if (lon && lat) {
				var lonLat = window.dataox.lonLat(map, lon, lat);
				var label = options.window || e.attr('data-label');
			} else
				throw new Error("Couldn't determine lon and lat for map " + domElement.id);

		 
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

	$('.dataox-autocomplete').each(function(i, e) { dataox.autocomplete(e); });
	$('.dataox-map').each(function(i, e) { dataox.map(e); });
});
