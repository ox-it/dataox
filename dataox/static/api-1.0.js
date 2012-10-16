$(function() {
	if (window.dataox == undefined)
		window.dataox = {};

	$.extend(window.dataox, {
		staticURL: $('body').attr('data-dataox-static-url') ||"https://static.data.ox.ac.uk/",
		sparqlURL: $('body').attr('data-dataox-sparql-url') ||"https://data.ox.ac.uk/sparql/",
		searchURL: $('body').attr('data-dataox-search-url') || "https://data.ox.ac.uk/search/",
		uriLookupURL: $('body').attr('data-dataox-uri-lookup-url') || "https://data.ox.ac.uk/doc/",
		defaultZoom: 14,
		osmTiles: 'https://static.data.ox.ac.uk/osm-tiles/${z}/${x}/${y}.png', // OpenStreetMap
		ocmTiles: 'https://static.data.ox.ac.uk/ocm-tiles/${z}/${x}/${y}.png', // OpenCycleMap
		transportTiles: 'https://static.data.ox.ac.uk/ocm-tiles/${z}/${x}/${y}.png', // OpenCycleMap Transport
		mapquestOpenTiles: 'https://static.data.ox.ac.uk/mapquestopen-tiles/${z}/${x}/${y}.png', // MapQuest Open
		locationQuery: ["SELECT * WHERE {",
		                "  [SELECTOR]",
		                "  OPTIONAL { ?uri skos:prefLabel|rdfs:label ?label }",
		                "  OPTIONAL {",
		                "    ?uri org:subOrganizationOf* ?withSite . ?withSite [SITE] ?site .",
		                "    NOT EXISTS {",
		                "      ?uri org:subOrganizationOf* ?intermediate .",
		                "      ?intermediate org:subOrganizationOf+ ?withSite ; [SITE] ?intermediateSite",
		                "    }",
		                "  }",
		                "  BIND(IF(BOUND(?site), ?site, ?uri) AS ?place)",
		                "  OPTIONAL { ?place skos:prefLabel|rdfs:label ?placeLabel }",
		                "  OPTIONAL {",
		                "    ?place spatialrelations:within* ?withGeo . ?withGeo geo:lat ?lat ; geo:long ?lon .",
		                "    NOT EXISTS {",
		                "      ?place spatialrelations:within* ?intermediate .",
		                "      ?intermediate spatialrelations:within+ ?withGeo ; geo:lat ?intermediateLat ; geo:long ?intermediateLon",
		                "    }",
		                "  }",
		                "  OPTIONAL {",
		                "    ?place spatialrelations:within* ?withAdr . ?withAdr v:adr ?adr .",
		                "    OPTIONAL {",
		                "      ?withAdr skos:prefLabel|rdfs:label ?containerLabel",
		                "    }",
		                "    OPTIONAL { ?adr v:street-address ?streetAddress }",
		                "    OPTIONAL { ?adr v:extended-address ?extendedAddress }",
		                "    OPTIONAL { ?adr v:locality ?locality }",
		                "    OPTIONAL { ?adr v:postal-code ?postalCode }",
		                "    OPTIONAL { ?adr v:country-name ?countryName }",
		                "    NOT EXISTS {",
		                "      ?place spatialrelations:within* ?intermediate .",
		                "      ?intermediate spatialrelations:within+ ?withAdr ; v:adr ?intermediateAdr",
		                "    }",
		                "  }",
		                "}"].join("\n"),
		getElement: function(e) {
			if (typeof e == "string")
				return $(document.getElementById(e));
			if (typeof HTMLElement == "object" ? e instanceof HTMLElement : typeof e == "object" && e.nodeType == 1)
				return $(e);
			return e;
		},
		generatedIdIndex: 0,
		generateId: function() {
			return 'dataox-element-' + window.dataox.generatedIdIndex++;
		},
		// Autocomplete. See https://data.ox.ac.uk/docs/api/autocomplete.html
		autocomplete: function(e, options) {
			options = options || {};

			/* If false, we use the more minimal 'autocomplete' format,
			 * otherwise we ask for full search results                 */
			options.fullContent = !!(options.fullContent || options.focus || options.select);

			e = window.dataox.getElement(e); // get the jQuery-wrapped version
			var obj = e.get(0);              // and the original DOM object

			searchURL = options.searchURL
			         || e.attr('data-dataox-search-url')
			         || window.dataox.searchURL;

			// build the default params for AJAX calls
			var defaultParams = {format: options.fullContent ? 'json' : 'autocomplete'};
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
					if (options.fullContent)
						e.val(data.hits.total ? data.hits.hits[0].label : originalVal);
					else
						e.val(data ? data[0].label : originalVal);
				}, window.dataox.jQueryDataType);
			}
			e.autocomplete({
				source: function(request, callback) {
					$.get(searchURL, $.extend({}, defaultParams, {
						q: request.term + '*'
					}), function(data) {
						if (options.fullContent) {
							for (var i=0; i<data.hits.hits.length; i++) {
								data.hits.hits[i] = data.hits.hits[i]._source;
								data.hits.hits[i].value = data.hits.hits[i].uri;
							}
							callback(data.hits.hits);
						} else
							callback(data);
					}, window.dataox.jQueryDataType);
				},
				minLength: 2,
				focus: function(event, ui) {
					e.val(ui.item.label);
					if (options.focus)
						options.focus(event, ui);
					return false;
				},
				select: function(event, ui) {
					e.val(ui.item.label);
					h.val(ui.item.value);
					if (options.select)
						options.select(event, ui);
					return false;
				}
			});
		},
		lonLat: function(map, lon, lat) {
			return new OpenLayers.LonLat(lon, lat)
				.transform(new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
				           map.getProjectionObject());
		},
		mapLayers: {
			"openstreetmap": function() { return new OpenLayers.Layer.OSM("OpenStreetMap", window.dataox.osmTiles) },
			"opencyclemap": function() { return new OpenLayers.Layer.OSM("OpenCycleMap", window.dataox.ocmTiles) },
			"mapquest-open": function() { return new OpenLayers.Layer.OSM("MapQuest Open", window.dataox.mapquestOpenTiles) },
			"transport": function() { return new OpenLayers.Layer.OSM("Transport", window.dataox.transportTiles) },
			"google-physical": function() { return new OpenLayers.Layer.Google("Google Physical", {type: google.maps.MapTypeId.TERRAIN})},
			"google-streets": function() { return new OpenLayers.Layer.Google("Google Streets", {numZoomLevels: 20})},
			"google-hybrid": function() { return new OpenLayers.Layer.Google("Google Hybrid", {numZoomLevels: 20, type: google.maps.MapTypeId.HYBRID})},
			"google-satellite": function() { return new OpenLayers.Layer.Google("Google Satellite", {numZoomLevels: 22, type: google.maps.MapTypeId.SATELLITE})}
		},
		// Maps. https://data.ox.ac.uk/docs/api/maps.html
		map: function(e, options) {
			options = options || {};
			e = window.dataox.getElement(e);
			var domElement = e.get(0);
			if (!domElement.id)
				domElement.id = window.dataox.generateId();

			if (e.attr('data-layers'))
				options.layers = e.attr('data-layers').split(" ");
			else
				options.layers = options.layers || ["openstreetmap"];

			options.map = new OpenLayers.Map(domElement.id, { controls: [] });
			options.map.addControl(new OpenLayers.Control.Navigation());
			options.map.addControl(new OpenLayers.Control.Attribution());
			if (options.layers.length > 1)
				options.map.addControl(new OpenLayers.Control.LayerSwitcher());

			for (var i=0; i<options.layers.length; i++) {
				var layer = options.layers[i];
				if (typeof layer == "string")
					layer = window.dataox.mapLayers[layer]();
				if (typeof layer != "object")
					continue;
				options.map.addLayer(layer);
			}

			options.markers = new OpenLayers.Layer.Markers( "Markers" );
			options.map.addLayer(options.markers);

			if (!options.places) options.places = [];

			options.zoom = options.zoom || e.attr('data-zoom');
			options.sitePredicate = options.sitePredicate || e.attr('data-site-predicate') || 'org:hasPrimarySite';
			options.selector = options.selector || e.attr('data-selector');

			var lon = options.lon || e.attr('data-lon');
			var lat = options.lon || e.attr('data-lat');
			if (lon && lat)
				options.places.push({
					lon: lon,
					lat: lat,
					label: options.label || e.attr('data-label')
				})

			var uris = [];

			var oxpointsID = options.oxpointsID || e.attr('data-oxpoints-id');
			if (oxpointsID) uris.push("http://oxpoints.oucs.ox.ac.uk/id/" + oxpointsID);

			var uri = options.uri || e.attr('data-uri');
			if (uri) uris.push(uri);

			var oxpointsIDs = options.oxpointsIDs || (e.attr('data-oxpoints-ids') ? e.attr('data-oxpoints-ids').split(" ") : []);
			for (var i=0; i<oxpointsIDs.length; i++)
				uris.push("http://oxpoints.oucs.ox.ac.uk/id/" + oxpointsIDs[i]);

			var otherURIs = options.uris || (e.attr('data-uris') ? e.attr('data-uris').split(" ") : []);
			for (var i=0; i<otherURIs.length; i++)
				uris.push(otherURIs[i]);

			if (options.selector || uris.length) {
				var query = window.dataox.locationQuery.replace("[SELECTOR]", options.selector || "VALUES ?uri { [URIS] }")
                                                       .replace("[URIS]", "<" + uris.join("> <") + ">")
				                                       .replace(/\[SITE\]/g, options.sitePredicate);
				window.dataox.sparql(query, function(data) {
					var newPlaces = {};
					for (var i=0; i<data.results.bindings.length; i++) {
						var binding = data.results.bindings[i];
						if (!newPlaces[binding.place.value])
							newPlaces[binding.place.value] = {}
						for (var field in binding)
							newPlaces[binding.place.value][field] = binding[field].value;
					}
					for (var placeURI in newPlaces) {
						var newPlace = newPlaces[placeURI];
						if (!(newPlace.lon && newPlace))
							continue;
						if (newPlace.uri == newPlace.withAdr && newPlace.containerLabel)
							delete newPlace.containerLabel;
						newPlace.address = [newPlace.containerLabel, newPlace.streetAddress, newPlace.extendedAddress, newPlace.locality, newPlace.postalCode, newPlace.CountryName];
        				// Remove any elements of the address that are missing.
        				for (var i=newPlace.address.length-1; i>=0; i--)
        					if (!newPlace.address[i]) newPlace.address.splice(i, 1);
        				options.places.push(newPlace);
					}
					window.dataox._mapShowPlaces(options);
				})
			} else if (options.places)
				window.dataox._mapShowPlaces(options);
		},
		_mapShowPlaces: function(options) {
			var size = new OpenLayers.Size(21,25);
			var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
			var icon = new OpenLayers.Icon(window.dataox.staticURL + 'marker.png', size, offset);

			for (var i=0; i<options.places.length; i++) {
				var place = options.places[i];
				place.lonLat = window.dataox.lonLat(options.map, place.lon, place.lat);
				place.marker = new OpenLayers.Marker(place.lonLat, icon.clone());
				options.markers.addMarker(place.marker);
				if (place.placeLabel && place.label && place.placeLabel != place.label)
					place.compositeLabel = place.label + " (" + place.placeLabel + ")";
				else
					place.compositeLabel = place.label || place.placeLabel;
				if (place.compositeLabel)
					$(place.marker.icon.imageDiv).attr('title', place.compositeLabel);
			}

			if (options.places.length == 0) {
				options.map.setCenter(window.dataox.lonLat(0, 0), 1);
			} else if (options.places.length > 1) {
				options.map.zoomToExtent(options.markers.getDataExtent(), false);
			} else {
				options.map.setCenter(options.places[0].lonLat, options.zoom || window.dataox.defaultZoom);
			}

			if (options.complete) options.complete(options);
		},
		supportsCORS: ('withCredentials' in new XMLHttpRequest()),
		jQueryDataType: ('withCredentials' in new XMLHttpRequest()) ? 'json' : 'jsonp',
		sparql: function(query, callback) {
			$.ajax({
				url: $('body').attr('dataox-sparql-url') || window.dataox.sparqlURL,
				type: "GET",
				data: {
					query: query,
					format: "srj",
					common_prefixes: "on"
				},
				dataType: window.dataox.jQueryDataType,
				success: callback
			});
		}
	});

	$('.dataox-autocomplete').each(function(i, e) { dataox.autocomplete(e); });
	$('.dataox-map').each(function(i, e) { dataox.map(e); });
});
