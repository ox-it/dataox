var map = null;

var endpointURL = "/data.ox.ac.uk/sparql/";
var docURL = "/data.ox.ac.uk/doc/";
var thumbnailURL = "/data.ox.ac.uk/thumbnail/"

var placeQuery = [
	"SELECT ?type ?typeLabel ?uri ?label ?lat ?long ?rootOccupant ?rootOccupantType WHERE {",
	"  VALUES ?types { rooms:Building oxp:Site } .",
	"  ?type rdfs:subClassOf* ?types ;",
	"    rdfs:label ?typeLabel .",
	"  ?uri a ?type ;",
	"    skos:prefLabel ?label ;",
	"    geo:lat ?lat ; geo:long ?long .",
	"  OPTIONAL {",
	"    VALUES ?rootOccupantType { oxp:Museum oxp:College oxp:Hall oxp:Division oxp:Library } .",
	"    ?uri (org:primarySiteOf|^org:hasPrimarySite) ?occupant .",
	"    ?occupant (org:subOrganizationOf|^org:hasSubOrganization)* ?rootOccupant .",
	"    ?rootOccupant a ?rootOccupantType .",
	"    NOT EXISTS {",
	"      ?occupant (org:subOrganizationOf|^org:hasSubOrganization)+ ?intermediateOccupant .",
	"      ?intermediateOccupant (org:subOrganizationOf|^org:hasSubOrganization)+ ?rootOccupant ;",
	"        a ?rootOccupantType .",
	"    } ",
	"  }",
	"}",
].join("\n");

window.onresize = function(event) {
	$('#container').height(window.innerHeight - $('header').height() );
	$('nav').height($('#container').height());
	$('aside').height($('#container').height() - 20);
	$('#placeList').height(window.innerHeight - $('header').height() - $('#navHeader').height() - 41);
}

function getLonLat(lon, lat) {
	return new OpenLayers.LonLat(lon, lat)
		.transform(new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
			map.getProjectionObject()); // to Spherical Mercator Projection
}

var iconSize = new OpenLayers.Size(32, 37);
var iconOffset = new OpenLayers.Pixel(-(iconSize.w/2), -iconSize.h);
		
var icons = {
    museum: "museum_archeological",
    college: "townhouse",
    hall: "townhouse",
    library: "library",

	uas: "workoffice",
    humanities: "highschool",
    mpls: "museum_science",
    msd: "medicine",
    socsci: "family",

    unknown: "pin-export",
}
for (var i in icons) 
    icons[i] = {
    	normal: new OpenLayers.Icon(staticURL + "maps/icons/" + icons[i] + ".png", iconSize, iconOffset),
    	inverted: new OpenLayers.Icon(staticURL + "maps/icons/" + icons[i] + "-inverted.png", iconSize, iconOffset)
    }

function getIcon(binding) {
	if (!binding.rootOccupant)
		return icons.unknown;
    var rootOccupant = binding.rootOccupant.value;
    var rootOccupantType = binding.rootOccupantType.value;
    if (rootOccupantType == "http://ns.ox.ac.uk/namespace/oxpoints/2009/02/owl#Museum")
		return icons.museum;
	if (rootOccupantType == "http://ns.ox.ac.uk/namespace/oxpoints/2009/02/owl#Library")
		return icons.library;
	else if (rootOccupantType == "http://ns.ox.ac.uk/namespace/oxpoints/2009/02/owl#College")
		return icons.college;
	else if (rootOccupantType == "http://ns.ox.ac.uk/namespace/oxpoints/2009/02/owl#Division") {
		if (rootOccupant == "http://oxpoints.oucs.ox.ac.uk/id/23232639")
			return icons.mpls;
		else if (rootOccupant == "http://oxpoints.oucs.ox.ac.uk/id/23233551")
			return icons.humanities;
		else if (rootOccupant == "http://oxpoints.oucs.ox.ac.uk/id/23232714")
			return icons.socsci;
		else if (rootOccupant == "http://oxpoints.oucs.ox.ac.uk/id/23233560")
			return icons.msd;
		else if (rootOccupant == "http://oxpoints.oucs.ox.ac.uk/id/23233564")
			return icons.uas;
		else
			return icons.humanities;
	} else
		return icons.unknown;
}

var places = {};
var lonLats = {};
var center = null;
var everything = null;
var markers = null;

$(function() {
	window.onresize(null);
	map = new OpenLayers.Map("map", { controls: [] });
	map.addLayer(new OpenLayers.Layer.OSM());
	map.addControl(new OpenLayers.Control.Navigation());
	map.addControl(new OpenLayers.Control.KeyboardDefaults());
	map.addControl(new OpenLayers.Control.Attribution());

	center = getLonLat(-1.258, 51.752);
	map.setCenter(center, 13);
	
	$('form').submit(search);
	
	showEverything();
});

function showEverything() {
	if (!everything) {
		$.get(endpointURL, {query: placeQuery, format: 'srj', common_prefixes: 'on'}, function(data) {
			everything = data;
			showEverything();
		});
		return;
	}

	if (markers)
		map.removeLayer(markers);
	markers = new OpenLayers.Layer.Markers( "Markers" );
	map.addLayer(markers);

    var placeUL = $('<ul/>').addClass("places");
	var bindings = everything.results.bindings;
	bindings.sort(function(a, b) { return a.label.value > b.label.value; });
	for (var i in bindings) {
		var binding = bindings[i];
		binding.lonLat = getLonLat(parseFloat(binding.long.value),
								   parseFloat(binding.lat.value));
		if (binding.lonLat in lonLats)
			lonLats[binding.lonLat].bindings.push(binding);
		else {
			var markerIcons = getIcon(binding);
			var marker = new OpenLayers.Marker(binding.lonLat, markerIcons.normal.clone());
			lonLats[binding.lonLat] = {
				bindings: [binding],
				marker: marker,
				icons: markerIcons,
			}
			markers.addMarker(marker);
			marker.events.register("click", marker, showLonLat(binding.lonLat));
		}
		if (binding.uri.value in places)
			places[binding.uri.value].push(binding);
		else {
			places[binding.uri.value] = [binding];
			placeUL.append($('<li/>')
			    .attr('data-uri', binding.uri.value)
				.text(binding.label.value)
				.click(showPlace(binding.uri.value)));
		}
		
	}
	$('#placeList').empty().append(placeUL);
}

function search() {
	var form = $(this);
	$.get(form.attr('action'), {
		q: form.find('#q').val(),
		format: 'json',
		page_size: 1000,
	}, function (data) {
		var matched = {};
		for (var i in data.hits.hits)
			matched[data.hits.hits[i]._source.uri] = true;
		$('#placeList li').each(function() {
			$(this).css('display', $(this).attr('data-uri') in matched ? "block" : "none");
		});
		for (var i in lonLats) {
			var lonLat = lonLats[i];
			var display = false;
			for (var j in lonLat.bindings) {
				if (lonLat.bindings[j].uri.value in matched) {
					display = true;
					break;
				}
			}
			lonLat.marker.display(display);
		}
		var bounds = markers.getDataExtent();
   		map.zoomToExtent(bounds, true);
	});
	
	return false;
}

function showPlace(uri) { return function(event) {
	showSidebar();
	var lonLat = places[uri][0].lonLat;
	var marker = lonLats[lonLat].marker;
	marker.setUrl(lonLats[lonLat].icons.inverted.url);
	//marker.inflate(2);
	map.panTo(lonLat);
	center = lonLat;
}; }

var sidebar = null;
var sidebarXHR = null;

function showSidebar() {
	if (!sidebar) {
		sidebar = $('<aside/>');
		$('#container').css('margin-right', 300).prepend(sidebar);
		window.onresize();
		map.panTo(center);
		//setTimeout(function() { map.panTo(center);}, 10);
	}
}

function showLonLat(lonLat) { return function(event) {
	showSidebar();
	var item = lonLats[lonLat];
	sidebar.empty().append($('<h2/>').text(item.bindings[0].label.value));
	sidebarXHR = $.get(docURL, {uri: item.bindings[0].uri.value, format: 'json'}, function(data, status, xhr) {
		if (xhr != sidebarXHR) return;
		if (data.v_adr) {
			var adr = data.v_adr[0];
			var address = [];
			if (adr['v_street-address']) address.push(adr['v_street-address'][0]);
			if (adr['v_extended-address']) address.push(adr['v_extended-address'][0]);
			if (adr['v_locality']) address.push(adr['v_locality'][0]);
			if (adr['v_postal-code']) address.push(adr['v_postal-code'][0]);
			sidebar.append($('<div/>').addClass('address').append(address.join('<br>')));
		}
		if (data.foaf_depiction) {
			var depictionUL = $('<ul/>').addClass('depictions');
			for (var i in data.foaf_depiction) {
				var depiction = data.foaf_depiction[i];
				if (depiction._uri)
					depictionUL.append($('<li/>').append(
						$('<img/>')
							.attr('data-url', depiction._uri)
							.attr('alt', '')
							.attr('src', thumbnailURL + "?width=200&height=120&url=" + encodeURIComponent(depiction._uri))));
			}
			sidebar.append(depictionUL);
		}
	});
}; }
